# Contract — derived objects on the wire

## The shape

`deliveredAttachmentSchema`'s media arm — the outbound-only shape chapter 4.14 created — gains
one optional property:

```
{
  type: "media",
  media_id: uuid,
  state: "pending" | "ready" | "rejected",
  thumbnail?: {
    media_id: uuid,
    width: number,
    height: number
  }
}
```

`attachmentSchema` — what a **sender** writes — is unchanged. A sender must not declare a
rendition, for the same reason 4.14 established for `state`: it is a fact the platform produces.

## Invariants

1. **`thumbnail` is absent, never null.** A client's question is whether a smaller one exists.
   The reason it does not exist is on the row, not on the wire (R6).
2. **`thumbnail` implies `state === "ready"`.** A rendition is made before the verdict that
   moves the parent to `ready`, so no other state can carry one. Asserted in both directions.
3. **`thumbnail.media_id` is fetched through the same door as the parent** —
   `GET /v1/media/:mediaId` — and authorised through the parent's referencing channels.
4. **A rendition addressed directly, by a caller that could not read its parent, is refused
   identically to an id no object has.** Same body, same status, differing only in
   `request_id`. This is FR-MED-08's rule for indistinguishable refusals, which 4.11 built for
   the attach path and 4.12 for delivery.
5. **A rendition may not be attached to a message.** The attach predicate refuses it, and the
   refusal is the same `media_not_available` a foreign object gets — a refusal naming the cause
   would report that somebody else's rendition exists.
6. **A rendition never appears as an attachment's `media_id`.** Only as `thumbnail.media_id`.
7. **`width` and `height` are the rendition's own**, not the parent's, because the point of
   sending them is a box a client can reserve before the bytes arrive.

## Doors this changes

4.14's lesson was that the door set is derived by the compiler and not by hand: a hand list of
three and a second of six were both wrong, and one door `tsc` cannot see at all because its
return type is inferred. The same derivation is re-run here rather than re-read — **the
previous answer is a fact about the previous shape.**

Every door that returns a `messageSchema` returns the new field, because `messageSchema`
embeds `deliveredAttachmentSchema`. That includes real-time delivery, history, the send
response, the edit response and resume. The derivation is recorded in `doors.txt` at
implementation time, as 4.14 did.

**The field is optional, so the compiler will not name the construction sites**, which is the
exact opposite of 4.14's `state` and has to be compensated for. `state` was made required
precisely so `tsc` would list every place a message is built. An optional property is silently
correct everywhere, so the derivation here is a runtime assertion over a delivered payload at
each door, not a build error — and that is weaker. It is recorded as weaker rather than
presented as equivalent.

## What an older client does

**Adding an optional property to the delivered arm is a strict-parse break for a client built
against the previous protocol.** `messageSchema` embeds `deliveredAttachmentSchema`, whose media
arm is `mediaArm.extend(...)` over a `z.strictObject` — so an unknown key is a refusal of the
whole message, not of the key. A client on the older build receiving `thumbnail` refuses the
message.

**The durable path is safe and the client path is not, and the difference is deliberate.**
`outbox/event.ts:391` and `:436` read off the queue with `forwardedAttachmentSchema`, whose last
arm is `z.looseObject({ type })`, so a new writer's field falls past both strict arms and is
accepted — a rolling deploy does not `term()` anything. That escape hatch exists for forwarding
and not for clients, which is 4.14's design working as intended rather than an oversight here.

**Nothing in this repository can catch the client half.** `packages/outsider` is the
external-perspective suite and it does `JSON.parse(...) as { type: string }` — a cast, not a
parse — so it will keep passing whatever the schema does. Recorded as a gap rather than solved,
the way 4.14 recorded 060-10's rolling-deploy window: building frame versioning for one optional
property is not this chapter's trade.

## What does not change

- No new error code. A refused rendition reuses the existing refusals.
- No new route. The delivery door already takes a media id.
- No new subject or frame. A rendition is made before the parent's verdict, so 4.14's
  `media.updated` already announces the moment a client should look again — and it carries the
  thumbnail on the next read, not in the frame. **The frame stays a notification, not a
  payload**, which is the optimisation-over-a-floor shape FR-MED-07 was amended into.
