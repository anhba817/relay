# Research — chapter 3.24, attachments

**Every number here was taken from the tree, not carried.** Chapter 3.23's most expensive
finding was a shape published in a document that nobody read under a name everybody checked,
and its cheapest wins came from asking the repository a question with a yes-or-no answer.

## R1 — The column exists, is typed as nothing, and has one writer that nulls it

`services/api/src/db/schema.ts:378` declares `attachments: jsonb("attachments")` — nullable,
no default, no shape. Present since chapter 2.1.

Three references in the whole platform, and none of them writes a value:

    repository.ts:4560   a comment in `deleteMessage` quoting SAD §342
    repository.ts:4710   `attachments: null`, in the tombstone UPDATE
    schema.ts:378        the declaration

`sendMessage`'s INSERT at `repository.ts:4189` lists `id`, `channelId`, `sequence`, `userId`,
`text`, `metadata`, `idempotencyKey`. **No attachments.** The column has never held a value.

## R2 — The wire has no field for it, and the protocol says so in the wrong tense

`packages/protocol/src/frames.ts:15` — `messageSchema` is a `strictObject` over exactly six
keys: `id`, `channel`, `seq`, `user`, `text`, `created_at`. A payload carrying an
`attachments` key is refused today, by design.

`frames.ts:14`, one line above it, reads:

> metadata/attachments/edit/tombstone fields arrive with Part 2/4

The edit and tombstone halves arrived in Part 3. **FR-MSG-11 is P2**, which is Part 3;
§4.14's hosted media is P3, which is Part 4. The sentence schedules a P2 clause for the later
phase, and it has been there since chapter 1.3. FR-018 exists because **no checker reads
prose** — chapter 3.23 found four sentences in this state and could only fix them by naming
each one in a requirement.

## R3 — The blast radius, measured

**Definition, stated because chapter 3.23 lost a re-count to not having one**: occurrences of
the identifier `text` on **non-comment** lines, in the ten files that build or carry a message
payload. Attachments follow `text` almost everywhere it goes.

    packages/protocol/src/frames.ts                             2
    packages/protocol/src/internal.ts                           2
    services/api/src/messages/messages.schema.ts                3
    services/api/src/messages/messages.service.ts               5
    services/api/src/messages/messages.controller.ts            9
    services/api/src/internal/internal.controller.ts            2
    services/api/src/internal/backfill.controller.ts            3
    services/api/src/db/repository.ts                          36
    services/api/src/outbox/event.ts                            3
    services/gateway/src/session.ts                             5
                                                        total  70

Not all seventy move. The number is the search space, and it says the same thing 3.21 and 3.23
found about their own counts: **a shape that rides beside `text` touches every door a message
has.** Four doors write one: the public send, the socket's send through
`internal.controller.ts`, the idempotent-retry replay, and the resume backfill's mapping.

## R4 — Five read paths return a message and they do not agree on columns

    repository.ts:5227  listMessages          id, channel_id, seq, user, text, created_at,
                                              edited_at            <- the history route
    repository.ts:5043  getMessageByIdempotencyKey
                                              id, channel_id, seq, text, created_at
                                              <- the retry replay, and it drops `user`
    repository.ts:4451  editMessage's read     id, userId, text, seq, createdAt, author
    repository.ts:4618  deleteMessage's read   + metadata, deletedAt
    repository.ts:5359  listMessagesRaw        id, text, seq — a test-only helper, five
                                              call sites, all in `idempotency.itest.ts`

Plus `listChannelsForUser`'s `last_message`, which is `{sequence, text, user, created_at}` —
a sixth shape, and the one the channel listing renders.

**FR-006 and FR-009 land on the first two. FR-011 lands on the second**, which is the one
that already omits a field the others carry.

## R5 — The event and the analytical column

`outbox/event.ts:16`'s `MessageCreatedData` is `{id, channel_id, seq, user, text, created_at}`.
Chapter 3.23 made `message.updated` reuse it verbatim and wrote FR-008a to keep them
identical, so **an attachments field added here lands on three event types at once**.

`docs/05-sad.md:608` publishes `attachment_count UInt8` on the ClickHouse `message_events`
table. That table is Part 4's and unbuilt. FR-017 asks only that the count be derivable, which
it is by construction if attachments are stored as an ordered list.

`consumer/recorder.ts:25` says in its own comment: *"Identifiers and counts only — never
`event.data.text`. A tenant's message body has no business in the platform's own logs
(NFR-SEC-06)."* **An attachment URL is closer to a body than to an identifier**, and the same
rule applies to it.

## R6 — Two URL precedents, and they disagree for a reason

    users.schema.ts:54          avatar_url: z.string().url().max(2048)
    webhooks.service.ts:188     new URL(raw) + protocol !== "https:" + a blocked-host list

The webhook check is strict **because Relay fetches that URL** — the blocked ranges are an
SSRF control. Relay never fetches an attachment URL, so that half does not apply.

What does apply is the half `avatar_url` skips.

## R7 — `z.url()` accepts `javascript:`, and this was measured rather than read

Run against the repository's own zod (**4.4.3**), both spellings:

    z.string().url()   z.url()
      true               true      https://example.test/a.png
      true               true      http://example.test/a.png
      true               true      javascript:alert(1)
      true               true      data:image/png;base64,iVBORw0KGgo=
      true               true      file:///etc/passwd
      true               true      ftp://example.test/a.png
      true               true      vbscript:msgbox(1)
      false              false     //example.test/a.png
      false              false     /relative/a.png

**Both accept every scheme.** They refuse a relative path and nothing else.

Two consequences:

- **FR-004's scheme check is the whole of the protection, not a belt beside braces.** An
  attachment validated with `z.url()` alone reaches a client as `javascript:alert(1)`, and a
  client that renders attachments is the one place this platform's data becomes somebody
  else's execution context.
- **`avatar_url` accepts `javascript:` today.** Its own comment argues that the field's name
  promises a URL — and the validator behind that promise delivers less than the comment
  assumes. Not this chapter's field and not this chapter's fix; `gaps.md` gets it, because it
  was found by running the validator rather than by reading it.

## R8 — The attachment shape, and why a discriminated union now

FR-003b asks for a union from the first version. The argument is chapter 3.23's, one level
down: **a kind that cannot share a payload type cannot share a shape.** An external-URL
attachment carries a `url`; a `media_id` attachment carries an id and, per FR-MED-07, a
*state* the platform maintains. They have one field in common and it is the discriminator.

Adding an arm to a `discriminatedUnion` is additive for every consumer that switches on the
discriminator. Widening a single object with `url?` and `media_id?` — both optional, one
required — is a shape that cannot say "exactly one of these", and Part 4 would have to
tighten it, which is the breaking change FR-020 forbids.

## R9 — What an edit does to attachments (FR-016)

Chapter 3.23's edit takes a body of exactly one field and appends `prior_text` to
`message_edits`. FR-MSG-07 says editing changes message **text**.

The narrow reading is the one the schema already implements: **an edit changes text and leaves
attachments alone.** Making attachments editable would need a second history column or a
second table, and FR-MSG-07 asks for neither.

What the chapter owes is a test that an edit does not *clear* them — the failure mode is not
"cannot edit attachments" but "editing the text silently drops the photograph", which an
`UPDATE ... SET text = ?, attachments = ?` written without care produces.

## R10 — The empty-string decision, and the five places it does not disturb

`text = ""` and `text IS NULL` are different values. Chapter 3.23 chose the null as its
tombstone predicate, and the places that branch on it read `text === null` or
`isNull(messages.text)` — none of them treats `""` as absent. So an attachments-only message
is a live message to every one of them without a line changing.

**The cost, stated because it is real:** the empty string now means two things — a message
sent with no words, and a message sent with attachments and no words. Nothing distinguishes
them and nothing needs to; a reader asking "does this message have text" gets the same answer
for both, which is *no*.
