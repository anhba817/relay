# Contracts — 043

Three published surfaces change and one internal surface gains a rule. No route is added,
no route is removed, and no request or response shape gains or loses a field.

Each contract below states what a caller sees **before** and **after**, because every one of
them is a refusal a customer can already trigger and get the wrong answer to.

## Files

| File | Surface |
|---|---|
| `socket-message-send.md` | The public WebSocket `message.send` frame |
| `rest-user-profile.md` | `PATCH`/`POST` on the user profile, `avatar_url` |
| `rest-webhook-endpoints.md` | Webhook endpoint create and update |
| `close-codes.md` | The six WebSocket close codes and where each is documented |

## The rule every one of them follows

A refusal caused by the caller names the caller's mistake. `ProtocolErrorFilter` derives a
code from 400, 401, 403 and 404 and answers `internal_error` for anything else, so a 422
that does not name its code tells the customer that Relay failed. Chapter 3.24 established
the shape for getting this right — `protocolError(code, message, status, field?)` — and
these contracts apply it to four surfaces that predate it.
