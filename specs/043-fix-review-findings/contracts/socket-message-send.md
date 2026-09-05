# Contract — the public WebSocket `message.send` frame

## What changes

The published maximum message length becomes enforceable at the socket. Nothing about the
frame's shape changes.

## Before

    message.send { idem_key, channel, text, attachments? }

`text` is declared `z.string()` with no bound. A 100 KB text passes the gateway's frame
schema, is held in memory, becomes an internal HTTP request, and is refused by the api's
`internalSendRequestSchema`, which bounds it at 8,000. The client learns — one hop late, and
by way of a code derived from the api's answer.

## After

`text` carries the same maximum as the other two send doors, imported from one definition.

| Case | Response |
|---|---|
| `text` within the maximum | unchanged |
| `text` over the maximum | an `error` frame carrying a registered code, a message, `docs_url`, `request_id`, and `field: "payload.text"` |
| over-long `text` sent | **no internal request is made** |

## What a client sees differently

The error code for this one case changes, because the refusal now comes from the gateway
rather than from the api. The frame's shape does not change: `errorFrameSchema` has
published `field` since chapter 1.3 and `sendError` has accepted it since chapter 3.24.

## Why the bound is imported rather than restated

Three schemas that happen to agree are three schemas that will one day disagree. Chapter
3.24 found the sharper form of this: `editMessageBodySchema.text` was
`sendMessageBodySchema.shape.text`, so relaxing the send's floor silently relaxed the edit's.
The lesson recorded there is that two schemas that must **differ** cannot share a reference —
and its converse is this one. Three doors that must **agree** must not each hold a literal.

## Verification

Send the same over-long text to all three entry points. All three refuse. `grep` for the
maximum's digits across the protocol package and the api returns exactly one definition.
