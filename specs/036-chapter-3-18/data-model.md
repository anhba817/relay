# Data model — chapter 3.18

**No schema change. No column, no table, no migration, no constraint.** Chapter 3.17 added two
columns and two check constraints to `users`; this chapter adds nothing to PostgreSQL. Every
entity below already exists, and the work is that one more process is allowed to emit one of them.

## The fan-out payload — `Message`

Already defined, already validated, already shared. `packages/protocol/src/frames.ts:15`:

    messageSchema = z.strictObject({ … })     Message = z.infer<typeof messageSchema>  (:145)

Six fields, and the api must publish exactly these six:

| field | source on the send path | note |
|---|---|---|
| `id` | the committed row | |
| `channel` | `committed.channel_id` — **renamed in the payload** | the frame's field is `channel` |
| `seq` | assigned by the repository inside the transaction | |
| `user` | the sender | non-null for every new message **since chapter 3.17** |
| `text` | the committed text | `null` means a tombstone, and a tombstone is not published |
| `created_at` | the committed row | |

**`z.strictObject` is the reason this list is exhaustive.** The delivery side parses with
`messageCreatedSchema.shape.payload.safeParse`, logs `fanout.invalid_payload`, and **returns** — an
invalid payload is dropped, not repaired and forwarded. So an api publishing `{…, environment_id}`
would deliver nothing at all, and the send would still return `201`.

**Only half of that is tested.** `fanout.itest.ts:128` — *"drops a payload the contract does not
allow instead of forwarding it"* — proves the drop, using `seq: -1`, an invalid **value**. The
extra-key case follows from `strictObject` rather than from any assertion, and the first draft of
this document cited that test for it. **A seventh field is the mistake an api publisher is most
likely to make** (`environment_id` and `channel_id` are both in scope at the publish site, and
`channel_id` is the wrong name for the `channel` field), so the extra-key case is worth its own
test rather than an inference.

**Chapter 3.17 is what makes a REST-sent message publishable.** `user` is `z.string().min(1)`, and
before 3.17 a message sent with an API key had no sender. A publisher written one chapter earlier
would have had nothing to put in that field, and every REST send would have failed validation at
the far end — silently, per the paragraph above. Worth a sentence in the chapter: the two features
are ordered, and not by accident.

## The subject — `chan:{channel_id}`

One subject per channel, so an instance receives only frames it can deliver. Currently
`services/gateway/src/fanout.ts`; moving to `packages/protocol` (R3).

**The subject is the delivery filter, and it is the only one.** There is no membership read in the
delivery path — an instance is subscribed because a session named the channel at connect time
(R5). This is the fact behind the plan's largest open risk, and it is a data-model fact rather than
a code detail: *the authority for "may this socket hear this channel" is a snapshot taken at
connect, held in a subscription, with nothing that invalidates it.*

## State transitions

None. A message is created, and creation is the only transition with a producer:
`message.updated` and `membership.changed` have zero producers outside tests, and nothing writes
`messages.edited_at` or `messages.deleted_at` (measured during `/speckit-specify`). FR-RTM-05 names
six event kinds; this chapter delivers one because one exists.

## What is deliberately not modelled

- **Presence.** Chapter 3.19 (spec FR-017, principle VII).
- **Delivery receipts or acks on the fabric.** At-most-once is the design (ADR-07, principle IV);
  adding an ack would make Redis a source of truth.
- **A dedupe key on the fabric.** Consumers of the *event spine* must deduplicate on event `id`
  (principle IV); the fan-out is not the spine. The gateway's `!committed.duplicate` guard is what
  prevents a retried send from being delivered twice, and it is a guard at the publisher, not a
  check at the consumer.
