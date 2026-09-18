# Contract — the upload slot

Written before the work. Chapter 4.2's lesson about `contracts/` is that it is the artifact
nothing else reads, so every claim here is one a command can drive.

---

## `POST /v1/media` — request an upload slot

**Authentication**: a user token or an API key. With a user token the row carries the user; with
an API key it does not, and FR-MED-06 later distinguishes them.

**Request**

    {
      "filename":  "holiday.jpg",
      "mime_type": "image/jpeg",
      "bytes":     2097152
    }

**Response — 201**

    {
      "media_id":   "<opaque>",
      "state":      "pending",
      "upload_url": "http://…/relay-media/<key>?X-Amz-Algorithm=…&X-Amz-Signature=…",
      "expires_at": "<15 minutes from now, ISO-8601>"
    }

`upload_url` is derived, not stored. `expires_at` is what the store will enforce, published so a
client can decide whether to reuse it — **the store is authoritative and the field is a courtesy.**

**Refusals**, each with its own code and each writing no row:

| status | code | condition |
|---|---|---|
| 415 | `media_type_not_allowed` | `mime_type` outside the ten allowed |
| 413 | `media_too_large` | `bytes` over the kind's cap — image 10 MB, audio 25 MB, video 100 MB |
| 402 | `media_storage_exhausted` | the environment's committed bytes plus `bytes` exceeds its cap |

**The statuses are proposals and the codes are the contract.** A client branches on the code;
the status is what a proxy sees. Tests assert the code — `webhooks.itest.ts` passed for four
chapters while the body said `internal_error`, and only the code could have caught it.

---

## The signed URL, and what is checked about it

Measured against `quay.io/minio/minio` before any of this was planned:

| property | how it is checked |
|---|---|
| a client can upload with it and no credentials | `curl -X PUT --upload-file f "$URL"` → **200**, with no auth header |
| no byte reaches the api | the api's own request log shows the slot request and nothing else |
| it expires | a URL whose `X-Amz-Expires` has passed → `AccessDenied · Request has expired`, **from the store** |
| it cannot be altered | one character changed in `X-Amz-Signature` → **400** |
| the bucket is not public | an unsigned GET of a stored object → **403** |
| the same signer reads | a signed GET returns the exact bytes — 45 of them, in the probe |

**The last two are FR-MED-08's preconditions**, checked here because they are free here and
because a later chapter that discovers the bucket is world-readable discovers it after publishing.

---

## What this contract does not offer

- No `PUT /v1/media/{id}` — bytes do not come through us (ADR-13).
- No `ready` state and no way to reach one. FR-MED-03 verifies and FR-MED-04 scans.
- No download URL. FR-MED-08's signed delivery is a later chapter, and the probe above only
  establishes that the mechanism exists.
- No `media_id` accepted on a message. The `{ type: "media" }` arm keeps refusing with
  `media_not_available` until 4.11, which is what `codes.ts:204` already says will happen.
