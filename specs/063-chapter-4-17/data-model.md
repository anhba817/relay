# Data model — chapter 4.17

This feature introduces no entity, no column and no message type. What follows is the state a
recipient can observe, written down because the journey asserts on it and because two of these
shapes have never been read from outside the platform.

## 1 · The attachment, as a recipient receives it

Measured from `GET /v1/channels/{id}/messages` on 2026-10-01, after the deployed worker ran:

```json
{
  "type": "media",
  "media_id": "6ba0e8be-b17c-4e78-8bf7-fd1a31dc90ff",
  "state": "ready",
  "thumbnail": { "media_id": "fd63e7ec-…", "width": 320, "height": 240 }
}
```

| field | who put it there | what the journey asserts |
|---|---|---|
| `type` | the sender (4.11's union arm) | present on the send response and in history |
| `media_id` | the sender | the same id the slot issued |
| `state` | 4.14, from `media_objects.state` | `pending` at send, `ready` after the worker, `rejected` on the refusal path |
| `thumbnail` | 4.15 | present once the rendition exists, absent before and for a non-image |

**`thumbnail` carries an id a recipient did not ask for**, which is what makes step 9 of the
journey a question a client would really have: it is the only place the platform hands out a
media id that no message names.

## 2 · The three states, and what each means to someone outside

| state | how it is reached | what a link request answers |
|---|---|---|
| `pending` | the slot was issued; the sweep has not run, or the bytes were never uploaded | refused |
| `ready` | the worker scanned the bytes and the declaration held | **200**, a signed URL |
| `rejected` | the scan or the verification refused the bytes, which were then destroyed | refused |

**The two refusals are the same answer.** 4.12 made every refusal on this route
byte-identical apart from `request_id`, so a caller holding a guessed id learns nothing — and
one consequence is measured in research R6: **with the worker stopped, an uploaded object and an
object that never existed give the same 404.**

## 3 · What the journey observes, and through what

The seal permits no workspace import, so every observation is a published route or a URL the
platform signed.

| step | surface | what it proves |
|---|---|---|
| slot | `POST /v1/media` | 4.10 — the slot is issued and the quota charged |
| upload | the signed `PUT` | 4.10 — the client reaches the store directly (ADR-13) |
| send | `POST /v1/channels/{id}/messages` | 4.11 — the attachment is permitted; 4.14 — it carries `pending` |
| verdict | *no surface* — observed through the next read | 4.13 — the deployed worker scanned real bytes |
| history | `GET /v1/channels/{id}/messages` | 4.14 — the state reaches a reader; 4.15 — so does the thumbnail |
| link | `GET /v1/media/{id}` | 4.12 — authorisation follows the message |
| bytes | the signed `GET` | the whole path: what comes back is what went in |
| thumbnail | `GET /v1/media/{rendition_id}` | 4.15 — a rendition's reachability is its parent's |

| the frame | `${ws}/v1/ws?token=` | 4.14 — a recipient holding a stale `pending` is told when it changes |

**AND THE FRAME CARRIES THREE FIELDS, NOT THE ATTACHMENT.** Measured:

```json
{ "media_id": "9555d52b-…", "channel": "23ef218a-…", "state": "ready" }
```

No thumbnail, no bytes, no message id. A client learns **that** the state changed and re-reads
history to learn what it changed to in full — which is why the journey asserts both the frame
and the payload §1 shows, rather than treating one as evidence for the other.

**A SUBSCRIBER MUST BE A MEMBER OF THE CHANNEL, EVEN A PUBLIC ONE.** Measured: without the
members call, the socket receives `connection.ack` and `presence.changed` and nothing else.
`channelVisibleTo` governs who may READ an object (4.12); membership governs who is SENT a
frame, and the two are different questions that the word "public" makes look like one.

**There is no surface for "has the worker run yet".** The journey learns the verdict by reading
the message again, which is exactly what a client would do and is the reason the wait is a poll
with a deadline rather than a sleep.

## 4 · State transitions the journey drives

```
            POST /v1/media                 the signed PUT              the deployed worker
   (none) ──────────────────▶ pending ──────────────────▶ pending ──────────────────▶ ready
                                  │                                          │
                                  │  no upload                               │  bytes contradict
                                  ▼                                          ▼
                              pending for ever                            rejected
                       (and FR-MED-10 reaps it after 24 h)        (bytes destroyed, row kept)
```

**The middle arrow changes nothing observable**, and that is the chapter's subject: an object
that was uploaded and an object that was not are the same `pending` until the worker runs.
4.13 built the sweep because nothing tells the platform the upload finished.

## 5 · What this feature does not model

- **No renderer.** FR-MED-09's *"renders as an explicit rejection marker"* needs a client, and
  there is none. The state reaching a recipient is the whole of what can be tested.
- **No metering.** 4.16's records travel a different route through a process no deployment
  starts; the journey does not wait on them.
- **No new error code.** Every refusal on this path already exists and is already named.
