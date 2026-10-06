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

## Outbound

| | before | after |
|---|---|---|
| every `channel` field | the Relay identifier | **the customer's identifier** |
| `membershipChangedSchema` on a ban | `"*"` | `"*"` — unchanged, not a channel |
| the session response's channel list | keys | **identities** |
| a resume cursor the server mints | keyed by key | **keyed by identity** |

## Inbound

| | behaviour |
|---|---|
| a send naming a channel by identity | lands in that channel |
| a send naming it by key | **keeps working** — 4.22's shape, and R4's reason |
| a resume cursor keyed by uuid | **accepted**, or constitution II is broken silently |
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
- **No new frame kind, and no new field on an existing one.** Strict payloads reject
  unknown fields, so adding one is a two-sided change — and nothing here needs it.
