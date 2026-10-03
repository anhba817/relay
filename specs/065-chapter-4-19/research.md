# Research — chapter 4.19

Everything below was measured against the composed platform on 2026-10-03, before the plan
was written. Where a number appears, the command that produced it is beside it.

---

## R1 — The schema already states the gap, and states it as a property rather than a loss

`message_edits` carries its own explanation of why a deletion writes nothing:

> FR-MSG-07: what the message said before this edit. NOT NULL, and that has a consequence the
> chapter meets rather than works around: **a deletion writes no row here, because a tombstone
> has no text to preserve.** FR-010 refuses an edit on a tombstone instead of defining what its
> history would say.

**The second clause is the one to read twice.** *A tombstone has no text to preserve* is true
of the row **after** the deletion and false of the moment before it. `deleteMessage` holds
`row.text` in scope — it branches on `row.text === null` to detect an already-deleted message
— so the text is in hand at the write site and nothing is looked up to get it.

So the gap is not a limitation the design ran into. It is a sentence that reads like one.

**Decision**: the chapter's first job is to correct that comment, whatever else it does. A
comment that explains an absence as a necessity is worth more than a missing row, because it
stops the next person asking.

## R2 — FR-MSG-08 already says a deletion is not a destruction

This is the clause that settles whether preserving the final text is permitted:

> **FR-MSG-08**: Deleting a message shall replace its content with a tombstone retaining
> sequence number, author, timestamps, and deletion metadata. **Hard deletion shall occur only
> via the compliance deletion endpoint.**

The second sentence is explicit. Erasure — FR-MOD-04, row 22 — is the only path that destroys,
and it is a different clause with a different actor: a moderator removes a message, an end user
exercises a right.

**So the current behaviour is the one in tension with FR-MSG-08, not the proposed change.**
Losing the final text at deletion is a hard deletion of exactly one version, performed by the
moderation path, which the clause reserves for the compliance endpoint.

**Decision**: the chapter preserves the final text, and FR-MSG-08 is the citation. No clause
amendment is needed for the preservation itself.

**Alternatives considered.** *Leave it and record the gap* — defensible, and it is what four
chapters have done by not noticing; refused because the clause reserving hard deletion to one
endpoint makes this a correctness question rather than a feature request. *Preserve it only
for application-credential deletions* — no clause distinguishes them for this purpose, and a
rule that depends on who deleted makes the recoverable history depend on something a reader
cannot see.

## R3 — Where the final version goes: three options, and the third is the interesting refusal

**A. A row in `message_edits`.** The text is there, the read is there, the tenancy scope is
there, and the primary key `(message_id, edited_at)` already orders versions. What it needs is
a way to say *this version ended because the message was deleted* rather than *because it was
edited*, and `edited_at` becomes a misleading name for a deletion row.

**B. A separate `message_versions` table.** Clean names, and a reader assembling a message's
history must union two tables that hold the same kind of row. Chapter 4.15 made this call the
other way for renditions — *"ONE TABLE, NOT TWO. Every door that acts on media reads
`media_objects`"* — and the argument transfers: every door that asks what a message said reads
this one.

**C. A column on `messages` holding the final text.** Refused, and the reason is the clause
rather than the shape: FR-MSG-08 says a deletion *replaces its content with a tombstone*. A
tombstone that still carries the text is not a tombstone, and every read path that treats
`text === null` as *deleted* would have to learn a second rule. It also puts a version on the
row it is a version of, which is the shape constitution IV refuses.

**Decision**: **A**, with a column naming why the version ended.

**AND THE COLUMN IS NOT OPTIONAL**, for the reason chapter 4.14 measured: a required field
makes the compiler name every construction site, and an optional one names none. There is
exactly one existing writer (`editMessage`) and one existing reader (`listMessageEdits`), so
the bill is small and the guarantee is worth more than the saving. Chapter 4.15 paid the other
side of that trade and recorded it as weaker.

**Open for the plan to settle**: whether the instant column is renamed. `edited_at` is wrong
for a deletion row and renaming it touches a published response field (`edited_at` is in the
`/edits` body) — which is a contract change under CON-05's URL-versioning rule, where adding a
field is not. The cheap answer is to add the discriminator and leave the column name; the
honest answer may be that a reader of `edited_at: …, ended_by: "deletion"` is being told two
things that disagree.

## R4 — The key's collision risk, measured

The primary key is `(message_id, edited_at)` and `editMessage`'s own comment says a conflict
there is a loud failure rather than a silent drop. A deletion row adds a second kind of writer
to that key.

```
distinct (message_id, edited_at) pairs: 4859 over 4859 rows
```

No collisions in 4,859 rows. And a deletion cannot collide with an edit on the same message by
construction: FR-010 of chapter 3.23 refuses an edit on a tombstone, so every edit precedes
every deletion, and two writes at the same microsecond would need the edit and the delete to be
the same statement.

**Decision**: the key is unchanged. The plan asserts the ordering property rather than assuming
it, because *cannot collide by construction* is the kind of claim this project has had to
withdraw before.

## R5 — FR-MSG-07 says "immutable edit history" and nothing enforces it

Measured, against the table the clause names and the table chapter 4.18 shipped:

```
triggers on message_edits: NONE
update message_edits set prior_text = 'tampered' where false;   →  UPDATE 0   (accepted)

triggers on audit_log:     audit_log_append_only
```

> **FR-MSG-07**: … recording an **immutable** edit history with timestamps.

The word is in the clause and there is no mechanism. Chapter 4.18 built one for FR-MOD-03 a
chapter ago, measured that `REVOKE` is inert against a superuser, and narrowed the test that
forbade triggers in migrations — **so the mechanism, its justification and the clearance to use
it all exist**, and applying it here is a migration and a trigger rather than an argument.

**Decision**: **in scope, and the plan says why rather than treating it as adjacent tidying.**
This chapter is about what a tenant can recover about a removed message. A history that can be
edited is a history whose answer to that question is not evidence, and the chapter would
otherwise publish a recoverable final text into a table anybody with the database password can
rewrite — which is the sentence 4.18 refused to leave unsaid about its own log.

**Alternatives considered.** *Out of scope, recorded as a gap* — it is a different clause
(FR-MSG-07, not FR-MOD-01) and this project's rule is that a defect found in earlier work is
recorded with its bill rather than absorbed. Refused because the bill is one migration reusing
a mechanism that shipped last chapter, and because the chapter's own product depends on it:
preserving a final text is worth less in a table that is not append-only than the clause already
claims it is.

**AND THE SCOPE IS THE SAME SCOPE 4.18 PUBLISHED.** The trigger refuses the application and
refuses accident; `SET session_replication_role = replica` and `DROP TRIGGER` both still work.
The chapter states that once and does not restate it.

## R6 — `deleted_at` is absent from the history row, and the frame has it

```
GET …/messages          seq=3  text=null  user=…  created_at=…  edited_at=null
message.deleted frame   id, channel, seq, user, deleted_at
message.deleted webhook  … deleted_at …          the outbox row, same transaction
DELETE itself           204, empty body          carries nothing
```

Three surfaces describe the same event and one of them omits the instant. A client that was
offline when the deletion happened and catches up through history learns that the message is
gone and not when.

*(This table listed the `DELETE` response as carrying `deleted_at` until the seventh analysis
pass ran it. It answers **204 with an empty body** — `messages.controller.ts:447`: "the status
is 204 either way, so the guard is the only thing that can tell them apart". The webhook is
the second surface that carries it, and the asymmetry is sharper than this row claimed: the
caller that performed the deletion is told nothing.)*

**Decision**: add it to the history row. **This is a field addition rather than a reshape**,
which CON-05's URL-versioning rule treats differently — chapter 4.8 made the same argument
adding `has_more` and cited EIR-API-04's precedent.

**And the shapes already disagree in three ways**, which the addition makes worth recording
rather than fixing:

| | history row | `messageSchema` |
|---|---|---|
| the channel | `channel_id` | `channel` |
| `edited_at` | present | absent |
| `text` on a tombstone | `null` | `z.string()` |

Nothing parses the history response against `messageSchema`, so the divergence costs nothing
today and no instrument can see it. **The plan records it and does not converge them**: chapter
4.14 measured what making a field required costs across construction sites, and a reshape here
would be a breaking change where the addition is not.

## R7 — The ambiguity the fallback guards against has no instances

`deleteMessage` justifies `?? toIso(row.createdAt)` with *"a system message with a null text
and no `deleted_at`, which has existed since chapter 2.1"*. Counted:

```
messages with text IS NULL                       4,861
  of those, deleted_at IS NOT NULL (tombstones)  4,861
  of those, deleted_at IS NULL                       0
messages that still have text                  176,157
```

**Zero.** The branch may still be right — a development lane is not production, and a row
class that existed in chapter 2.1 may have been migrated away since — but the sentence is a
claim about data and the data disagrees.

**Decision**: measure it, record it, and **do not delete the branch**. Chapter 4.6 reached
100% branches by deleting two arms that could not run and one of them carried a comment
claiming a test drove it; the lesson there was that an unreachable arm should be *proven*
unreachable, and *this lane holds none* is not that proof. The chapter corrects the sentence to
say what was measured and where.

## R8 — The fence bill, counted before the work

Chapter 4.15's rule: count it in phase 1, where it can still change how the work is sequenced,
and expect it to be short because every file it misses arrives from a repair made afterwards.

```
repository.ts              52 pages
schema.ts                  34 pages
messages.service.ts        27 pages
messages.controller.ts     18 pages
messages.schema.ts         12 pages
frames.ts                  12 pages
messages.itest.ts          18 pages   analysis pass 2
vitest.coverage.config.mts 23 pages   analysis pass 6
```

Every one of these is published by pages this chapter does not own, so every hunk goes to
`fences/post-series.md` — 4.8's rule, and one rule for eight files beats a judgement per file.
Chapter 4.18 paid **49 hunks across 21 files** and six of those files arrived from repairs made
after its list was written; this list should be read as a floor.

**And it was read as a floor correctly: six became eight before a line of code was written.**
`messages.itest.ts` asserts an exact key set this chapter widens; `vitest.coverage.config.mts`
is edited by T067 in the last phase, after the chain has been taken to zero, which is the
sequence 4.18's first red CI run came from. **Neither was found by looking at the file list —
both came from asking what the work touches.**

## R9 — What the premise check means for the chapter's shape

Row 20's brief is FR-MOD-01 and FR-MOD-02 *via API key*, and the measurement says both are
substantially built: 204 on another author's message, tombstones in history, prior texts from
`/edits`, and that route already application-credential only.

**So the chapter's subject is not a surface. It is a sentence in a clause** — *complete
history* — and what the platform means by it. That is the same shape as 4.7's *"counts derived
from operational data"*, 4.16's *"(uploaded/deleted)"* and 4.17's *"renders as"*: the clause's
own words are the work.

**Decision**: the chapter opens with the arithmetic, because it is one line and it is the whole
argument. N edits then a deletion leaves N recoverable texts out of N+1. Zero edits leaves zero
of one.
