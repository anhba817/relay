# Contract — the `{ "type": "media" }` attachment arm

The surface this chapter changes is one arm of one array on one route that has existed since
chapter 2.2. No new route, no new field, no new header.

**`POST /v1/channels/:channelId/messages`** — `@Accepts("application", "user")`, unchanged.

---

## The arm, before and after

```jsonc
// before — parsed so the discriminator matches, then refused unconditionally
{ "type": "media", "media_id": "<any non-empty string>" }
// → 422 media_not_available
//   "hosted media is not available yet — attach an http or https url instead"

// after
{ "type": "media", "media_id": "<uuid>" }
// → 201, when the object is in the sender's environment, attachable by the sender,
//        and in state `pending` or `ready`
```

`media_id` is a UUID now. Research R3 measured what the looser shape costs once the arm accepts:
`invalid input syntax for type uuid` from the driver, which the error filter turns into a **500**.
A malformed id is a caller's mistake about JSON and answers `400 invalid_request` naming
`attachments.<n>.media_id`, which is what every other malformed field already does.

---

## The refusal

One code for all three conditions (research R4). Status **422**: the body is well-formed and
understood, and what cannot be done is the thing it asks for — chapter 3.24's own argument for the
422 this code replaces.

**And 422 joins the error filter's ladder in this chapter.** Analysis pass 1 measured that it is
not there: the rungs are 400, 401, 402, 403, 404, 413, 415 and 503, so an unnamed 422 answers
`internal_error`. Nothing is broken today because every 422 in the platform names its own code —
which is exactly the condition the ladder exists for the day it stops being true.

The code is named by **T006** and is not spelled here, so that one task owns the decision rather
than three documents carrying a guess. What the contract fixes is everything else about the body.

```jsonc
{
  "code": "media_not_attachable",          // the name T006 decides; the shape does not depend on it
  "message": "<one sentence, the same for all three>",
  "docs_url": "…",
  "request_id": "…",
  "field": "attachments.<n>"
}
```

**`field` names the attachment, not the id.** Chapter 3.24 settled this for the URL arm's
refinement — *"a caller with ten links is told which one"* — and the path stops at the object
because the whole attachment names something the caller may not attach, not because `media_id`
is malformed.

**The three conditions are indistinguishable.** Another tenant's id, another user's id, and an id
nobody owns produce byte-identical bodies apart from `request_id`. That is SC-002, and it is a
requirement rather than a nicety: the alternative is an existence oracle for a guessable UUID.

---

## What is removed

`media_not_available` leaves the registry and the error reference. The state it describes — *"the
platform cannot serve `media_id` yet"* — stops existing the moment the arm accepts, and the
registry's own entry instructs the deletion rather than a repurposing.

`protocolCode` stays in `ZodValidationPipe` with no user, and says so (research R5).

---

## What is unchanged, and is worth stating because a reader will look for it

- **The ten-attachment cap** counts media and URL attachments together. It always has: the cap is
  `z.array(attachmentSchema).max(10)` over the union.
- **A message may carry no text** when it carries an attachment. Chapter 3.24's rule.
- **The same id twice is two attachments.** Nothing compares them.
- **Delivery carries no attachment state.** FR-MED-07 is movement VI. A subscriber receives the
  attachment array as sent and learns nothing about whether the bytes have been checked.
- **A `media_id` is not yet fetchable.** FR-MED-08's signed delivery is row 13; this chapter makes
  a message able to name an object, not a recipient able to read one.
