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

| status | code | condition | retry? |
|---|---|---|---|
| 415 | `media_type_not_allowed` | `mime_type` outside the ten allowed | no — transcode |
| 413 | `media_too_large` | `bytes` over the kind's cap — image 10 MB, audio 25 MB, video 100 MB | no — compress |
| 402 | `media_storage_exhausted` | the environment's committed bytes plus `bytes` exceeds its cap | no — free space or raise the cap |
| 503 | `media_storage_unavailable` | the object store cannot be reached | **yes** |

**The fourth is the only transient one**, which is why it needs its own code rather than folding
into `internal_error`. `docs/05-sad.md:1062` specified it — *"Object storage lost … Upload slots
return a specific error"* — and a client that cannot tell it from the other three either retries
three refusals that will never succeed or abandons the one that would.

**The statuses are proposals and the codes are the contract.** A client branches on the code;
the status is what a proxy sees. Tests assert the code — `webhooks.itest.ts` passed for four
chapters while the body said `internal_error`, and only the code could have caught it.

**AND EACH STATUS NEEDS A LADDER ENTRY, NOT ONLY A NAMED THROW.**
`protocol-error.filter.ts` maps 400, 401, 403 and 404 and falls everything else through to
`internal_error`. All four statuses above are outside it, so they are correct only while every
thrower remembers to name its code. The filter's own comment calls that fallback *"a lie the
client cannot act on"* — twice, once for the 400 chapter 2.2 fixed and once for the 403 the
credentials chapter fixed. Four new statuses without ladder entries is four more.

---

## The signed URL, and what is checked about it

Measured against `quay.io/minio/minio` before any of this was planned:

| property | how it is checked |
|---|---|
| a client can upload with it and no credentials | `curl -X PUT --upload-file f "$URL"` → **200**, with no auth header |
| no byte reaches the api | the api's own request log shows the slot request and nothing else |
| it expires | a URL whose `X-Amz-Expires` has passed → `AccessDenied · Request has expired`, **from the store** |
| it cannot be altered | one character changed in `X-Amz-Signature` → **403 `SignatureDoesNotMatch`** |
| the bucket is not public | an unsigned GET of a stored object → **403** |
| the same signer reads | a signed GET returns the exact bytes — 45 of them, in the probe |

**The last two are FR-MED-08's preconditions**, checked here because they are free here and
because a later chapter that discovers the bucket is world-readable discovers it after publishing.
They hold for a bucket created **through the API** as well as for one made by hand — measured
separately, because the first probe made its bucket with `mkdir` and proved nothing about the
path the platform will actually take.

**And the bucket itself is signed the same way**, with a different canonical URI — `/{bucket}`,
no key segment. `PUT` 200, `HEAD` 200, and a second `PUT` answers `BucketAlreadyOwnedByYou`,
which is what lets the api create it on every boot rather than guarding with a flag.

---

## What this contract does not offer

- No `PUT /v1/media/{id}` — bytes do not come through us (ADR-13).
- No `ready` state and no way to reach one. FR-MED-03 verifies and FR-MED-04 scans.
- No download URL. FR-MED-08's signed delivery is a later chapter, and the probe above only
  establishes that the mechanism exists.
- No retry of a failed store call inside the api. `media_storage_unavailable` is reported, not
  worked around; the client holds the retry because the client holds the file.
- No `media_id` accepted on a message. The `{ type: "media" }` arm keeps refusing with
  `media_not_available` until 4.11, which is what `codes.ts:204` already says will happen.
