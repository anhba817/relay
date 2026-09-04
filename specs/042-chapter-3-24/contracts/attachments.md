# Contracts — chapter 3.24, attachments

## The shape

```
{ "type": "url", "kind": "image" | "audio" | "video", "url": "https://…" }
```

`strictObject`, so an unknown key is a refusal rather than a silent drop — the argument
`membershipFabricSchema` and `revisionFabricSchema` both make: a field added on one side of a
rolling deploy fails loudly on the other instead of vanishing.

A `discriminatedUnion` on `type` with one arm today. §4.14 adds `{"type": "media", …}`.

## Sending

    POST /v1/channels/{channelId}/messages
    body: { "text": "…", "attachments": [ … ], "metadata": …, "idempotency_key": …, "user": … }

- **`attachments` is optional.** Absent and `[]` mean the same thing and both store `NULL`.
- **201** the message, with `attachments` echoed in the order sent.
- **400** `invalid_request` with `field` naming the offender:
  - more than 10 (FR-005)
  - a `kind` outside the three (FR-002)
  - a URL whose scheme is not `http` or `https` (FR-004)
  - a URL longer than 2048 characters
  - `text` empty **and** no attachments (FR-019b)
- **422** `media_not_available` — a `{"type": "media"}` attachment (FR-003, FR-003a).

**Why 422 and its own code rather than a 400 naming the field.** A `media_id` attachment is
not malformed; it is a published part of FR-MSG-11 that this deployment cannot serve yet, and
a customer reading the clause will send one. `invalid_request` sends them to check their
syntax, which is correct. The status follows `webhooks.service.ts`'s precedent for a body
that parses and cannot be honoured.

**The same rules on the socket's send frame** (`message.send`) and on the internal hop
(`POST /internal/messages`), because a message sent through a socket and a message sent
through REST must be the same message.

**The two doors do not agree today, and the disagreement is checkable rather than remembered.**
`frames.ts:44` takes `idem_key: z.string().min(1).max(255)` and
`messages.schema.ts:13` takes `idempotency_key: z.string().uuid()` — different names, different
types, one concept. `packages/outsider/src/integrate.itest.ts` records paying for that in its
own comment: *"Two entrances, two idempotency contracts — the second run of this inverted test
failed on it."* **Attachments must not become the second such field**, which is why the bound,
the kinds and the scheme rule live in one module both doors import rather than in two schemas
that happen to match.

## Reading

    GET /v1/channels/{channelId}/messages

Every message carries `attachments`, an array, **never absent** (FR-007). A message sent
without them reads `[]`. A tombstone reads `[]` (FR-012).

## The wire

`message.created` and `message.updated` carry `attachments` on their `messageSchema` payload.
`message.deleted` does not, and its payload has no place for one — chapter 3.23 gave it an
identity with no text for the same reason (FR-013).

**Resume carries them** (FR-010). The backfill returns rows as they are now, so a client that
was away and a client that stayed connected hold the same message — the property chapter
3.23's FR-016 established for edits, applied to a field rather than a text.

## The events

`message.created` and `message.updated` webhook events carry attachments on their existing
`MessageCreatedData` payload. FR-008a of chapter 3.23 requires those two to stay identical,
so the field lands on both or neither.

**`message.deleted` carries none**, as it carries no text.

**The platform's own logs carry neither the URL nor the text** — `recorder.ts:25`, NFR-SEC-06.
A count is an identifier-shaped fact and is fine; a URL is closer to a body.

## What this contract does not promise

- **That the URL resolves.** Relay never fetches it, at send time or later. A 404, a private
  address, or a host that never resolves is indistinguishable from a working link here, and
  the platform says so rather than implying a check it does not make.
- **That the content is what the `kind` says.** Nothing probes it. FR-MED-04's scanning and
  FR-MED-05's thumbnails attach to hosted media, which is Part 4.
- **That an attachment can be edited.** FR-MSG-07 changes text. An edit leaves attachments as
  they were (FR-016).
