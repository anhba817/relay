# Research — chapter 4.11, "the half of the union that was refused"

Every row below was **run**, not reasoned about. Where a premise came back false, the false
version is kept beside the measurement.

---

## R1 · The specification's one flagged assumption is wrong, and 4.10 said so in advance

**The assumption, as the spec states it**: FR-MED-06's *"(for user tokens) was uploaded by the
sending user"* refuses a user token attaching an object whose `user_id` is NULL, because a NULL
was not uploaded by that user.

**Settled against it.** The clause's two sentences disagree, and the second one is narrower than
the first: *"Attaching another tenant's or **user's** media shall fail."* A NULL `user_id` is not
another user's media. It is nobody's, which in this schema means the tenant's.

**And chapter 4.10 wrote down what the nullable column is for**, in the controller that creates
the rows:

> *"A photo sent by a person and an attachment uploaded by a customer's backend are the same
> operation, and the difference shows up one chapter later, when FR-MED-06 asks whether the
> sender uploaded it. That question needs the row to remember which of the two asked, which is
> why `user_id` is nullable rather than filled in with something."*

**"Are the same operation"** is the sentence that decides it. Under the strict reading the two
operations are not the same at all: one produces an object any user of the tenant can attach and
the other produces one nobody can. The column was made nullable so the question could be asked;
answering "NULL always fails" makes the nullability pointless, because any sentinel would do.

**Decision**: three cases, not two.

    user_id = the sending user        attach permitted
    user_id = a different user        refused (the clause's second sentence)
    user_id IS NULL                   attach permitted — the tenant uploaded it

**And it leaks nothing.** The environment predicate is what constitution I needs; a tenant's own
object reaching a user of that tenant, in a channel that user can already post to, discloses
something the tenant chose to disclose by handing out the id.

**What the strict reading would have cost**: the normal server-side integration — a backend takes
the slot, hands the `media_id` to its client, the client sends the message — refused, with a code
saying the media belongs to another user when it belongs to the tenant the caller is part of.

---

## R2 · `ready` is unreachable, and the database says so by name

**Run**, against the lane's Postgres:

```text
INSERT INTO media_objects (…, state) VALUES (…, 'ready');
ERROR:  new row for relation "media_objects" violates check constraint
        "media_objects_state_check"
```

Chapter 4.10's migration carries `CHECK (state = 'pending')` and explains it: *"`ready` and
`rejected` arrive [with the worker] … a schema claiming states nothing in the platform can reach."*

**Decision**: the state predicate is written as FR-MED-06 reads — admit `pending` and `ready`,
refuse the rest — and its unreachable arms are named in the code rather than covered by a test
that cannot fail. The refusal above is the chapter's evidence, quoted.

**Rejected: widen the CHECK so a fixture can plant `ready`.** That is a schema claiming a state
nothing produces, which is the thing 4.10 refused, and it would buy a green assertion about a
transition no code performs. **Rejected: omit the state check until the worker ships.** The clause
says `pending` or `ready`; a check that admits everything is a different clause.

---

## R3 · A non-UUID `media_id` reaches the database and comes back as a 500

**Run**:

```text
SELECT id FROM media_objects WHERE id = 'not-a-uuid';
ERROR:  invalid input syntax for type uuid: "not-a-uuid"
```

The media arm accepts `media_id: z.string().min(1)`. Once the arm stops refusing, any non-empty
string reaches the lookup, Postgres raises `22P02`, and `ProtocolErrorFilter` answers **500
`internal_error`** — a caller-triggered 500, which is the filter's own definition of *"a lie the
client cannot act on"*.

**Decision**: the arm validates `media_id` as a UUID at the schema, so a malformed id is a **400
`invalid_request`** naming the field. That is the honest separation: a malformed id is a caller's
mistake about JSON, and a well-formed id nobody owns is the refusal R4 designs. It is also the
shape the platform already mints — `POST /v1/media` returns an id matching
`/^[0-9a-f-]{36}$/`.

**Rejected: catch the driver error in the repository.** It would turn one class of malformed input
into the wrong code, and the pattern generalises badly: the next column with a typed comparison
needs the same catch.

**Note what this does to the contract.** Tightening `media_id` narrows what the route accepts, and
nothing was accepted before — the arm refused unconditionally — so no caller can be relying on the
looser shape. Worth stating because CON-05 makes a breaking change a URL-versioning event, and
this is not one.

---

## R4 · The three refusals are one answer, and the send path already argues why

**Decision**: another tenant's id, another user's id, and an id nobody owns return the same code
and the same message.

`messages.service.ts` already records the pattern for the ban refusal: *"it is thrown before the
channel is resolved — so this refusal is the same for a channel that exists, one that belongs to
another tenant, and one that was invented. The gauntlet asserts exactly that pair."*

Distinguishing them would answer "that id exists, but not for you", which is a cross-tenant
existence oracle for a UUID a caller can guess at leisure. Constitution I.

**Rejected: three codes**, on chapter 4.10's *"a client acts on them differently"* argument. A
client acts identically on all three: stop using that id. The 4.10 argument held because retry was
right for exactly one of its four; here it is right for none.

---

## R5 · Deleting `media_not_available` orphans the mechanism it was built for

`codes.ts:207` instructs the deletion: *"§4.14 replaces the arm rather than this code … at which
point it is deleted, not repurposed."* Six places name it:

    packages/protocol/src/codes.ts:207           the entry
    packages/protocol/src/codes.test.ts:244-246  three assertions
    packages/protocol/src/attachments.ts:93      the refinement's params
    services/api/src/messages/messages.itest.ts  three assertions, the arm's refusal
    services/api/src/messages/zod-validation.pipe.ts:13   a comment citing it as the reason
    docs/08-error-reference.md                   its section

**And `protocolCode` has exactly one user** — `attachments.ts:93`. The pipe reads it so a schema
refinement can name a code other than `invalid_request`, and chapter 3.24 built that mechanism for
this one refusal. The new refusal cannot use it: it needs a database read, so it comes from the
service as a `protocolError`.

**Decision**: the mechanism stays, with no user, and says so. It is nine lines in the pipe, it is
taught, and it is the only way a schema refinement can carry a code — the next one that needs it
would otherwise rediscover the problem. This follows chapter 4.10's `service_unavailable`, kept as
the ladder's fallback with nothing throwing it and a comment explaining that.

**Rejected: delete the mechanism too**, on 4.4's *"a design in which a case cannot arise beats a
branch that handles it"*. That rule is about branches that rot; this is a general extension point
with one departing user, and deleting it would unteach a chapter to save nine lines.

**The comment at `zod-validation.pipe.ts:13` must change either way** — it cites a code that will
not exist. `gaps.md` 056-10's convention applies: it names what the mechanism is for rather than
who used it.

---

## R6 · The cap already counts both arms, and one thing is already true

`messages.schema.ts:40` is `z.array(attachmentSchema).max(MAX_ATTACHMENTS)`, and
`MAX_ATTACHMENTS` is 10. The cap is over the array, so a media attachment counts alongside a URL
attachment by construction. FR-012 needs a test, not a change.

`sendMessage` already writes inside `this.db.transaction`, so FR-011's *"read the media object
inside the transaction that writes the message"* is a placement rather than a new structure —
the same shape 4.10's `reserveMediaSlot` took, and for the reason the lint rule gives: the query
engine lives in the repository.

---

## R7 · The send route is already a gauntlet target, and it is the derivation's canary

`POST /v1/channels/:channelId/messages` is classified `write` and attacked. It is also
`CANARY_TARGET` — *"a route that has existed since chapter 2.2 … if the derivation cannot find
THIS, it has not found the mounted router."*

**So this chapter adds no target and the derivation will not find anything unclassified.** That is
worth saying because eight chapters running have been caught by that check; this one cannot be,
and the accounting direction that still applies is the second — an attack that exists and does not
cover the new identifier.

**Decision**: extend the existing `write` attack with a forged `media_id`, and plant a media object
for each tenant so an empty table cannot pass it. Chapter 4.8's finding, verbatim: *"an empty log
passes a leak check for the same reason an empty page does."*

---

## R8 · What is not built here, and why each one is a later chapter

- **Attachment state in delivery.** FR-MED-07 is `docs/12` row 15, movement VI. Adding a `state`
  field or a `media.updated` event here ships that chapter's surface with none of its checks —
  the mistake FR-016 stopped this chapter's predecessor from making in the other direction.
- **Verification.** FR-MED-03 is row 14. It is what makes `ready` reachable, which is why R2's
  arm cannot be tested now.
- **The unlink-and-sweep.** FR-MED-10 hard-deletes unreferenced objects 24 hours after a tombstone
  unlinks them. This chapter creates the first references, so it records what a second message
  referencing one object means for that sweep — nothing tracks reference counts, and
  `gaps.md` 056-1 already records that an unused slot is indistinguishable from an uploaded one.
- **Signed delivery.** FR-MED-08 is row 13. A `media_id` in a message is not yet a URL anybody can
  fetch.
