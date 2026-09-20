# Contract — the delivery URL

## The route

```
GET /v1/media/:mediaId
```

`@Accepts("application", "user")`, matching `POST /v1/media`. The path parameter is a UUID; a
malformed one is a **400 `invalid_request`** naming `mediaId`, which is the shape 4.11 built for
`attachments.<n>.media_id` and the reason the arm takes `z.uuid()` rather than a string.

## The answer

```
200 OK
{
  "url": "http://localhost:9100/relay-media/<env>/<id>?X-Amz-Algorithm=AWS4-HMAC-SHA256&…",
  "expires_at": "2026-09-19T16:04:11.000Z"
}
```

**One hour.** `expiresIn: 3600`, against the upload slot's `900`. Two validities for one object,
and both numbers belong in the chapter together — a reader who meets them a page apart assumes
one of them is a typo.

**The URL's host is whatever the api signed with**, which is `RELAY_MINIO_ENDPOINT` and not
`RELAY_MINIO_INTERNAL_ENDPOINT`. 4.11 split those because the host is inside the SigV4
signature; this route hands its URL to a **client**, so it takes the public one — the same arm
`presign` already uses for an upload slot, for the same reason.

## The refusal

```
404 Not Found
{
  "code": "not_found",
  "message": "no media object with that id is readable by this caller",
  "docs_url": "https://relay.example/docs/error-reference#not_found",
  "request_id": "…"
}
```

**One answer for three conditions** — another environment's object, an object referenced only in
a channel the caller cannot read, and an id no object has. Byte-identical apart from
`request_id`, asserted as one property over the whole body rather than as three tests that
happen to agree.

**No new code.** `not_found` exists, is documented, and is the error filter's 404 rung. A chapter
that adds a route and no vocabulary is unusual enough to assert: `check:errors` reads **34 codes,
34 sections** at the close, the same as 4.11.

**No `field`.** The upload slot's refusals name one because the caller sent a body with a wrong
value in it; here the id is in the path and there is only one thing it could be.

## The other door

**There is none, and that is the finding.** The gateway has no media surface. A socket client
that receives a `message.created` frame carrying `{ type: "media", media_id }` asks the **api**
for the URL over REST, exactly as a REST client does.

4.11 had three doors to check because `attachmentSchema` is embedded in three request schemas.
This chapter has one, because a delivery URL is not part of any frame — and `research.md` R5
checked that rather than assuming it.

## What the caller is not told

- **Whether the object exists.** That is the point of the single refusal.
- **Whether the bytes are there.** An object is `pending` until movement VI, and a URL for one
  whose upload never happened is well-formed and fetches a **404 from the store**. Relay signs
  arithmetic and never contacts the store on this path, so it does not know and does not guess.
- **Whether the URL will still work in five minutes.** It will, for an hour, **and that is true
  even if the caller is removed from the channel one minute from now.** The store checks a
  signature; it has never heard of a channel. Published as a cost of ADR-13 rather than hidden.

## What it costs the tenant

One `rest` operation per request. `operationsFor` returns `["rest"]` for every `/v1` path, so a
client rendering fifty images spends fifty of the tenant's budget. **Left counted** — 4.8 made
the same call for the request log and published the loop rather than routing around it, because
an exemption list is a hand-maintained table.

## The sixteen routes this chapter does not fix (T016b)

**A malformed uuid in a path parameter is a caller-triggered 500 on every shipped route that
takes one.** Measured against the composed api, with a control:

    GET /v1/channels/not-a-uuid/messages      500 internal_error
    GET /v1/channels/not-a-uuid               500 internal_error
    GET /v1/channels/<a random uuid>/messages 404 not_found        ← the control

The value reaches the driver, Postgres answers `invalid input syntax for type uuid`, and
`ProtocolErrorFilter` has no rung for it. The control is what makes this a claim about the
*shape* of the id rather than about the id being unknown.

    @Param("channelId")   13 routes
    @Param("messageId")    3
    @Param("mediaId")      1   ← this chapter's, validated
                          --
                          16 unvalidated before this chapter, 16 after

**Decision: they are recorded, not repaired.** The fix is one `z.uuid()` per parameter and the
bill is not the fix:

    services/api/src/messages/messages.controller.ts   18 titled fences   8 of the 16
    services/api/src/channels/channels.controller.ts    8                 7
    services/api/src/users/users.controller.ts          4                 1
                                                       --
                                                       30 fences across three published files

Thirty fences is thirty hunks, each of which has to anchor against the chain's state at its own
chapter, for a change that teaches nothing this chapter is about. 4.11 made the same call on
reference counting and filed 057-1; what stops that being an excuse is that the measurement goes
into `gaps.md` with the route counts, so the next chapter to touch a controller inherits a number
rather than a suspicion.

**The argument that nearly won.** *"A measurement is not a repair"* is what 049 wrote about
`check-lane-scope.py` after measuring a retarget and not landing it, and this is the same shape.
What decides it the other way is that the class is not this route's: the 500 predates the chapter
by sixteen routes and eleven chapters, and one chapter fixing sixteen routes in three controllers
it otherwise never opens is how a fence chain gets 1,576 diff lines to make one point.
