# Contracts — chapter 3.23

## Who may call each route, declared rather than checked

The controller declares `@Accepts("application", "user")` at class level
(`messages.controller.ts:64`), so **a route added to it inherits both credential classes**.
Two of the three below mean one of them, and the guard reads `getAllAndOverride`, so a
method-level declaration wins. `dev-token.controller.ts:51` already does this.

    PATCH :messageId          @Accepts("user")           an edit is the author's, and an
                                                         application principal has no author
    DELETE :messageId         (inherits both)            the author, or a tenant key (FR-012)
    GET :messageId/edits      @Accepts("application")    FR-023's audience is FR-MOD-01's

**Declared, not checked in the handler.** `credential.guard.ts:31` argues the case —
*"`@Accepts("platform")` DOES NOT COMPILE, and that is the point"* — and
`messages.controller.ts:59` names the alternative as the defect: a route that declared nothing
let the guard *"fall back to `EITHER`"*, which is how the gateway's credential reached
`POST /internal/dispatch/replay` in chapter 3.12. **There are exactly two principal kinds and
no key-acting-as-a-user shape**, so a declaration expresses each of these three exactly.

## The two routes

Both live on the channel's message resource, beside the existing send and history routes.

### Edit

    PATCH /v1/channels/{channelId}/messages/{messageId}
    body: { "text": "…" }

- **200** the updated message, in the same shape the send route returns.
- **400** the body is not a valid text.
- **403** `not_message_author` — the caller is not the author. **A tenant API key is also
  refused here** — FR-MOD-02 grants deletion of any message and is silent on editing, and
  silence is not permission. **Not the generic permission code**: no credential grants
  authorship, so that code's published remedy is advice nobody can act on (FR-022).
- **403** `message_deleted` — the message is a tombstone (FR-010).
- **404** the message is not in a channel this caller can see, or does not exist.

**AMENDED DURING PHASE 5. This section said 404 for a tombstone and the argument it gave was
false.** It read: *"A 410 on a message a caller may not edit would confirm the message
exists."* Nobody who may not edit the message ever reaches this refusal —
`repository.editMessage` checks authorship **before** it looks at the text, so a stranger is
refused with `not_message_author` whether the message is a tombstone or not. The only caller
who sees the tombstone answer is the author, and the author can read the message in history:
FR-011 (3.23) keeps deleted messages in their original position.

So a 404 here would tell a caller that a message they are looking at does not exist — and
that is **chapter 2.8's defect, in one resource with two verbs.** That chapter found `POST`
answering 404 for a channel `GET` answered 200 for, and its fix was to make the two agree:
*"one resource should not answer two ways depending on the verb."* A `GET` that returns the
tombstone beside a `PATCH` that says it is not there is the same disagreement.

`message_deleted` is a new error code, which makes two in one chapter — one more than the plan
expected. `codes.ts` applies that file's own test to it out loud: what a client does on this
code (stop offering an edit control, re-read history) differs from what it does on
`not_message_author` (never offer one), and 404, `forbidden` and `not_message_author` were each
rejected in writing.

**The rejected alternative is still 410**, for the reason the original paragraph gave: it says
*it was here and it is gone*, which is more than this api says anywhere. 403 with a specific
code says the same thing to the one caller entitled to hear it and nothing to anybody else.

The deletion route answers 204 for an already-deleted message (FR-009) because idempotence is
the requirement there; the edit route refuses.

### Delete

    DELETE /v1/channels/{channelId}/messages/{messageId}

- **204** the message is a tombstone now, whether or not it was one before (FR-009). The
  tombstone records **who** deleted it as well as when (FR-006a) — a tenant key may delete
  anybody's message, so the author it keeps is the writer and not the remover.
- **403** `not_message_author` — the caller is an end user who is not the author.
- **404** not visible to this caller.

**A tenant API key is permitted here irrespective of author** (FR-MOD-02).

### Read the edit history

    GET /v1/channels/{channelId}/messages/{messageId}/edits

- **200** `{ "edits": [ { "prior_text": "…", "edited_at": "…" }, … ] }`, **oldest first**.
- **403** the caller is an end user, **including the message's author** (FR-023a). What a
  message used to say is a moderation surface; that it was edited is not.
- **404** not visible to this caller, or no such message.

**A tenant API key only** (FR-023). The audience is FR-MOD-01's — *"retrieving any channel's
complete history, including tombstones and edit history, via API key"* — and this route closes
the per-message half of that clause. The channel-level "complete history" remains its own
chapter's.

**Empty is a 200, not a 404.** A message with no edits has an empty history, which is a fact
about the message rather than the absence of a resource.

## The frames

`message.updated` is unchanged and already published — payload is a `messageSchema`, carrying
the new text.

`message.deleted` **changes**, and it is the only schema this chapter edits:

    payload: {
      id, channel, seq, user,
      deleted_at: RFC 3339
    }

- **No `text` field.** A deleted message has no text, and an empty string would be
  indistinguishable from a message somebody sent blank.
- **`messageSchema` is untouched.** It has been published since chapter 1.3 and every other
  frame that carries a message keeps its contract.

## The webhook events

FR-WHK-02 names eight types and three exist. This chapter adds the fourth and fifth,
**spelled as the clause spells them**: `message.updated` and `message.deleted`.

The payload follows the existing envelope. The deleted event carries no text, for the same
reason the frame does not.

## What a client does

| It receives | It should |
|---|---|
| `message.updated` | replace the text of the message with that id; keep its position |
| `message.deleted` | render the position as removed content; keep the position |
| neither, because it was offline | re-read the range through history, which returns current state |

**The last row is the contract's one soft edge** and it is deliberate: a message older than a
client's resume cursor that changed while the client was away produces no frame and no
sequence gap. History is the repair, and it is the same repair Slack documents.
