# Contract — what each frame names

The chapter adds no frame and no field. It changes what one field in seven schemas
carries, in one direction, and widens what two accept.

## The seven

```
messageSchema                 channel     outbound
messageDeletedPayloadSchema   channel     outbound
mediaUpdatedSchema            channel     outbound
membershipChangedSchema       channel     outbound   — and ALL_CHANNELS ("*")
typingSchema                  channel     outbound
messageSendSchema             channel     INBOUND
typingSendSchema              channel     INBOUND
```

`channel` is `z.string().min(1)` in all seven and stays that way: **the type does not
change, the value does.** A schema that said `.uuid()` would have made this chapter a
breaking contract change; it does not, which is the one thing about the current
design that helps.

## The three that are not fields

`connectionAckSchema` names channels three more times and not once with a `channel`
field. Pass 1 found them; the first version of this contract had none of them.

```
revisions    z.record(channel, number)   frames.ts:83 · every ack, zeros included
cursor       z.record(channel, seq)      frames.ts:66 · the resume answer
truncated    string[] of channel ids     frames.ts:67 · FR-RTM-04's refetch list
```

**And the payload is a `z.strictObject` inside a `z.strictObject`**, so each of the
three is a contract change both sides must make together rather than a value a
client can absorb.

## Outbound

| | before | after |
|---|---|---|
| every `channel` field | the Relay identifier | **the customer's identifier** |
| `membershipChangedSchema` on a ban | `"*"` | `"*"` — unchanged, not a channel |
| the session response's channel list | keys | **identities** |
| a resume cursor the server mints | keyed by key | **keyed by identity** |
| `connection.ack.payload.revisions` | keyed by key | **keyed by identity** |
| `connection.ack.payload.truncated` | a list of keys | **a list of identities** |

## Inbound

| | behaviour |
|---|---|
| a send naming a channel by identity | lands in that channel |
| a send naming it by key | **keeps working** — 4.22's shape, and R4's reason |
| a resume cursor keyed by uuid | **accepted**, or constitution II is broken silently — and the thing that would break it is `resume.ts:80`, which FILTERS unknown keys out without a word |
| a resume cursor keyed by identity | accepted |
| an identifier the user may not hear | refused exactly as today, revealing nothing new |

**THE INBOUND AMBIGUITY HAS NO SHAPE TEST TO FALL BACK ON.** A channel path segment
either parses as a uuid or cannot — that is what let 4.22 decide by shape. A cursor
key is a string in a record and so is an identity, and an `external_id` may itself be
a uuid: 0 of 41,772 channels today, which 4.22 measured and did not forbid. How the
two are told apart is Phase 2's decision and this contract's one open row.

## What this contract does not offer

- **No retirement of the key on the socket.** Every connected client holds a
  uuid-keyed cursor. A window, a warning and a version belong to a later chapter.
- **No change to the subjects.** `subjectForChannel` and its four siblings derive
  from the key. A subject is not a thing a client sees.
- **No change to `internalSendRequestSchema.channel_id`.** It stays
  `z.string().uuid()`; that door is the gateway talking to the api, and the gateway
  translates before it knocks.
- **No change to `internalBackfillResponseSchema.channels`**, keyed by key, or to
  the cursors the gateway sends it. Internal, both directions.
- **`internalMembershipsResponseSchema.channel_ids` is the one open question here**
  — a second api→gateway contract carrying keys, called on a timer by the
  revocation backstop (`api-client.ts:202`). Whether it widens to pairs is T010's
  decision, because the backstop is also the cheapest place to refresh the map.
- **No change to `presence.changed`**, which carries `{user, state, transition}` and
  names no channel, and **none to `message.ack`**, which carries `seq` alone. Both
  were checked at pass 2 rather than assumed from the count of seven.
- **No new frame kind, and no new field on an existing one.** Strict payloads reject
  unknown fields, so adding one is a two-sided change — and nothing here needs it.
