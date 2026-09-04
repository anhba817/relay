# Data model — chapter 3.24, attachments

## The column, which already exists

    messages.attachments   JSONB   NULL          schema.ts:378, since chapter 2.1

**No migration.** The column is there, nullable, with no default and no shape. SAD §6.1
publishes it as `attachments JSONB` and says nothing more, so unlike chapter 3.23's
`message_edits` there is no published DDL to reproduce — and nothing to get wrong by not
reading it.

## What the reader gets, which is `unknown`

    messages.attachments   jsonb("attachments")   no .$type<>()   schema.ts:378

Drizzle infers a bare `jsonb()` as `unknown` on select. The compiler was asked rather than
assumed — a probe assigning `typeof messages.$inferSelect["attachments"]` to a `string[]`:

    error TS2322: Type 'unknown' is not assignable to type 'string[]'.

So no read path can hand this column to a `messageSchema` payload without first saying what it
is, and there are three ways to say it. The tree has already chosen twice:

    repository.ts:2788   metadata: row.metadata as Record<string, unknown>
    repository.ts:2859   metadata: sql<Record<string, unknown>>`${channels.metadata}`

`schema.ts` contains **zero** `.$type<>()` calls. This chapter adds none and uses the `sql<…>`
form at each read site:

    attachments: sql<Attachment[] | null>`${messages.attachments}`

The reason is not consistency for its own sake. `.$type<>()` is one claim covering every reader
of the schema, present and future; `sql<…>` is one claim per read site. **Neither validates
anything** — both are casts, and Postgres enforces no shape on a JSONB column. Putting the
claim at the read site keeps the number of unchecked assertions equal to the number of places
that actually read, which is three: `sendMessage`'s two return paths and
`getMessageByIdempotencyKey`'s select, both widened in phase 3, and the resume backfill's
mapping in phase 8.

**NULL and `[]` are different values and this chapter decides what each means.**

    NULL   the message has no attachments, or is a tombstone whose attachments were unlinked
    [ … ]  the message has attachments

The read paths return `[]` for both (FR-007), so a client never sees the difference. Storing
`NULL` rather than `[]` for a message sent without attachments keeps every row written before
this chapter — every message in the platform — valid without a backfill.

## The attachment

    kind   "image" | "audio" | "video"     FR-002, the three the clause names
    url    an absolute http/https URL      FR-003, FR-004

A discriminated union on a fourth field from the first version (FR-003b):

    { type: "url",      kind, url }              this chapter
    { type: "media",    kind, media_id, state }  §4.14, Part 4 — refused today

**The discriminator is `type` and not `kind`.** `kind` is the clause's word for what the
attachment *is* — a picture, a sound, a film — and both arms have one. `type` is what the
attachment *references*. Collapsing the two would make `kind: "media"` a category error and
leave Part 4 with no room.

**Ordered, and the order is the caller's.** FR-006 says attachments come back in the order
they were sent, on every path — the history route, the resume replay, and both socket paths. A
JSON array carries that for free; nothing sorts them and **nothing deduplicates them** (FR-021):
the same URL attached twice is two attachments, because every definition of sameness is a
decision a customer would have to be told about.

**No id of its own.** An attachment is not addressable: no route fetches one, deletes one, or
updates one. Giving it an id would be inventing a resource nothing asks for — and chapter
3.23's `message_edits` records what happens when a chapter invents a key the SAD did not
publish.

## Bounds

    at most 10 per message         FR-005, the clause's number
    url at most 2,048 characters   FR-023, taking `users.avatar_url`'s bound — the
                                   platform's only precedent for a stored URL
    scheme http or https only      FR-004 — and R7 measured that `z.url()` alone accepts
                                   `javascript:`, `data:`, `file:` and `vbscript:`

**The 4 KB metadata bound (FR-MSG-01) is not shared.** Attachments are not metadata, and none
of the three budgets constrains the others.

**The total a send can now carry, stated because this is the first field that multiplies:**

    text          8,000 characters      FR-MSG-01
    metadata      4 KB                  FR-MSG-01
    attachments   10 x 2,048 = 20,480   FR-005 and FR-023
                                        ────────
    about 28,500 characters before framing

**Against express's default JSON body limit of 100 KB**, which this api does not override, and
a `ws` server created as `new WebSocketServer({ noServer: true })` with **no `maxPayload`**, so
its default of 100 MiB applies. Nothing breaks and nothing is near a wall — and the arithmetic
of `10 × 2,048` is an implication of two bounds that nobody had multiplied. The next field with
a per-item bound should read this line before choosing one.

## The message's life, with attachments

    (nothing) --send-->  live          text and/or attachments, at least one of them
    live      --edit-->  live'         text changes, attachments UNCHANGED     (FR-016)
    live      --delete-> tombstone     text NULL, attachments NULL             (3.23)
    tombstone --read-->  []            every read path                         (FR-012)

**An edit leaves attachments alone**, which is FR-MSG-07 read narrowly: it says editing
changes message *text*. The failure this guards is not "attachments cannot be edited" but
"editing the text silently drops the photograph" — an `UPDATE … SET text = ?, attachments = ?`
written without care.

## What each read path returns

Derived from the code, and the shapes do not agree today — R4 counted six:

| Path | Today | After |
|---|---|---|
| `listMessages` (history, resume) | id, channel_id, seq, user, text, created_at, edited_at | + attachments |
| `getMessageByIdempotencyKey` (retry) | id, channel_id, seq, text, created_at | + attachments. **It also omits `user`, which is a pre-existing difference this chapter does not fix** |
| `listChannelsForUser.last_message` | sequence, text, user, created_at | unchanged — a preview shows what was said, and FR-CHN-09 asks for the most recent message rather than its contents |
| `listMessagesRaw` | id, text, seq | unchanged — a test-only helper with five call sites, all in `idempotency.itest.ts` |
| `editMessage`'s internal read | id, userId, text, seq, createdAt, author | unchanged — it writes text and returns the edited message |
| `deleteMessage`'s internal read | + metadata, deletedAt | unchanged — it nulls attachments and returns a tombstone |

**Two of the six change.** Naming the four that do not, and why, is what stops a later reader
assuming an omission.

## The empty-text rule

    text = ""      a message with attachments and no words          FR-019
    text = NULL    a tombstone                                      chapter 3.23

The two are different values, and every place that tests for a tombstone reads the null. **An
attachments-only message is a live message to all of them without a line changing** (R10).

**The cost, stated:** `""` now means two things — a message sent with no words, and a message
sent with attachments and no words. Nothing distinguishes them, and a reader asking *does this
message have text* gets the same answer for both.

**A message with neither text nor attachments is still refused** (FR-019b). The bound relaxes
because there is something else to carry, not unconditionally.
