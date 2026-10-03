# What a tenant can recover about a removed message — counted, with the clause beside each

SC-007 asks for a count rather than an adjective. Every row is *met*, *demonstrated*,
*unmet by decision* or *unreachable*, with where — the four verdicts chapters 4.11,
4.16 and 4.18 settled on, because *"supported"* hides the difference between a thing
that works and a thing nobody has run.

**Demonstrated** means a test attempts it and the platform answers; **met** means the
behaviour is there and the evidence is a measurement rather than an assertion.

---

## FR-MOD-01 — "any channel's complete history, including tombstones and edit history, via API key"

Five obligations, and the clause reads as one sentence.

| # | obligation | verdict | where |
|---|---|---|---|
| 1 | any channel's history, irrespective of membership | **MET before this chapter** | `channelVisibleTo(channelId, undefined)` — an application credential is the tenant reading, which sees everything it owns |
| 2 | including tombstones | **MET before this chapter** | `listMessages` has never had a predicate on `messages.text`; a tombstone comes back in its original position with `text: null` |
| 3 | including edit history | **MET before this chapter** | `GET …/messages/{id}/edits`, built in 3.23 |
| 4 | **and the text it held when it was removed** | **DEMONSTRATED here** | `versions.itest.ts` — three texts for a message edited twice and deleted, one for a message deleted with no edits. It was **two of three and zero of one** before this chapter |
| 5 | via API key | **MET before this chapter, asserted here for the first time** | `@Accepts("application")`; a user token gets 403 `wrong_credential_type`. Deleting the decorator answers that token **200 with the tenant's whole edit history** — the probe is in `versions.itest.ts` and nothing had checked the enforcing half |

**WHAT "COMPLETE" STILL DOES NOT INCLUDE**, named rather than left to be discovered:

- **the current text of a live message** — it has not stopped being current, so it is
  not a version; it comes from the channel's history, which the caller usually already
  has. Assembling every text a message ever held is **one request for a deleted
  message and two for a live one**, and the asymmetry is the shape of the data.
- **who ended a version** — the audit log's (FR-MOD-03, chapter 4.18), joined by
  nothing automatic. An entry exists only for an application credential's deletion, so
  a joined shape would be null for most rows and read as missing data.
- **what was attached** — FR-MED-10 unlinks a tombstone's attachments and versions hold
  text.
- **anything deleted before this chapter shipped.** Counted below.

## FR-MOD-02 — "deleting any message via API key, irrespective of author"

| obligation | verdict | where |
|---|---|---|
| a tenant key deletes a message it did not author | **MET before this chapter** | measured twice: chapter 4.18's premise check and this one's T005 — 204, another author's message |

No work. The chapter says so rather than re-deriving it.

## FR-MSG-07 — "recording an immutable edit history with timestamps"

| obligation | verdict | where |
|---|---|---|
| an edit history with timestamps | **MET since 3.23** | `message_edits`, `(message_id, edited_at)` |
| **immutable** | **DEMONSTRATED here, and SCOPED** | `0023`'s `BEFORE UPDATE OR DELETE` trigger. `UPDATE` and `DELETE` both refused through `psql`, the row surviving both |
| immutable to somebody holding the database password | **UNMET, published rather than omitted** | `SET session_replication_role = replica` and `DROP TRIGGER` both succeed, measured. ADR-35's scope, re-measured on a second table rather than assumed to transfer |

**The word was a description for six chapters.** Measured before `0023`: both verbs
succeeded, and `audit_log` had carried a guard since 4.18 while this table — holding
the same kind of evidence — had none.

## FR-MSG-08 — "a tombstone retaining sequence number, author, timestamps, and deletion metadata. Hard deletion shall occur only via the compliance deletion endpoint."

| obligation | verdict | where |
|---|---|---|
| the tombstone retains sequence, author, timestamps | **MET since 3.23** | the row survives; `listMessages` returns it in place |
| deletion metadata | **MET since 3.23** | `messages.metadata.deleted_by`, and the audit entry beside it since 4.18 |
| **hard deletion only via the compliance endpoint** | **MET here, and it was not before** | losing the final text at a moderation delete was a hard deletion performed by the moderation path. This is the clause the chapter is built on, and it needed no amendment |

---

## The boundary, counted

Measured on the development lane after the chapter applied and the lanes had run.

```
tombstones total                                      5,343
  final text RECOVERABLE — deleted since the chapter     283
  final text GONE FOR EVER — predate it                5,060
    of those, nothing recoverable at all               3,762
    of those, earlier texts survive                    1,298
```

**THE 1,298 ARE THE CASE A SINGLE NUMBER HIDES.** A tombstone with version rows looks
served — ask for its history and texts come back — and the one that matters, the text
on screen when the moderator acted, is not among them. Counting only the 3,762 with
nothing at all understates the boundary by a quarter, and this chapter's own spec made
that mistake until its sixth analysis pass.

**NO MIGRATION RECOVERS ANY OF THE 5,060.** A deletion before this chapter destroyed
the text; `0022`'s backfill writes `ended_by = 'edit'` on rows that already existed and
invents nothing. The chapter publishes the boundary rather than implying the history is
complete backwards.

## And what this chapter hands forward

```
messages that cannot be hard-deleted today            4,565
```

`message_edits_message_id_fkey` is `NO ACTION`, so a message with version rows refuses
a hard delete **before any trigger is consulted**. Every deletion from now on adds one
to that number, where only edited messages contributed before.

**Row 22's erasure meets two obstacles and the foreign key is the first.** `audit_log`
has one — its foreign key points at `environments` and nothing deletes those. Three
artifacts in this feature said the collision was *"exactly as the audit log does"*
until the third analysis pass ran the delete and read the error.

Retention (row 21) and erasure (row 22) are the two chapters that remove this data, and
**neither is built**: the same absent scheduler bounds both (ADR-28), which is the third
clause in this platform to be bounded by it after FR-ANL-06 and DR-17.
