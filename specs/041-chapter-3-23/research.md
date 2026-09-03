# Research — chapter 3.23

**Every finding below was read out of the repository or measured, and each says which.** The
distinction matters here more than usual: chapter 3.22's single most common defect was a
premise inherited from a predecessor's record and never re-run, three times in one chapter.

---

## R1 — Both frame kinds already exist, and the hand-off asked a question the tree had answered

`packages/protocol/src/frames.ts:63-77` publishes `message.created`, `message.updated` and
`message.deleted`, each `z.strictObject` with `payload: messageSchema`. They have been there
since chapter 1.3. Chapter 3.22's `ForwardRef` asked *"whether an edit and a deletion are one
event kind or two"*; the answer has been **two** for twenty-two chapters.

**Read, not derived.** This is the third consecutive chapter whose hand-off named a decision
already published — 3.21 assigned 3.22 a decision sitting at `docs/05-sad.md:574`, and 3.22
assigned this one a question `frames.ts` had settled. The pattern is now worth naming in the
chapter itself.

## R2 — The published payload cannot express a tombstone, and the running code says so twice

`messageSchema.text` is `z.string()` (`frames.ts:20`). A tombstone has no text. Two places
already refuse to publish one and name the constraint in their own comments:

    messages.controller.ts:194   "`messageSchema.text` is `z.string()`, not nullable, so a
                                 tombstone could not be published anyway"
    backfill.controller.ts:83    "A tombstone (FR-MSG-08) is not a creation. When deletes
                                 arrive in Part 4 they get `message.deleted`, and resume
                                 will carry that frame instead"

**The second comment is a promise this chapter has to keep or correct**, and the spec's
decision keeps half of it: deletes do get `message.deleted`, and resume does **not** carry
that frame — see R6.

## R3 — The columns exist; one table does not, and its absence is dated

`schema.ts` already has `messages.edited_at` (:382), `messages.deleted_at` (:383), a nullable
`text` and an `attachments` jsonb column (:377). `schema.ts:26` lists deliberate absences with
named arrivals, and one of them is **`message_edits` (edit chapter)** — this chapter.

`docs/05-sad.md:435` publishes the DDL for it, with `prior_text TEXT NOT NULL -- FR-MSG-07`.
`docs/05-sad.md:342`'s sequence diagram publishes the deletion:
`UPDATE message SET text=NULL, attachments=NULL, deleted_at=now()`.

**So the SAD prescribes both halves and this chapter implements rather than argues** — the
opposite of chapter 3.22, which had to argue a published row down. No ADR is expected. If one
becomes necessary the plan is wrong somewhere, and that is worth noticing early.

## R4 — Three read paths, three behaviours, all deliberate, none exercised by a writer

| Path | Behaviour with a null text | Where | Tested? |
|---|---|---|---|
| REST history | passes the row through | `messages.service.ts:176` → `repo.listMessages`, no text predicate | **no** |
| Internal backfill | drops the row; the sequence gap is the signal | `backfill.controller.ts:92` | yes, for the senderless half |
| Channel listing preview | reports a null text and still counts the unread | `repository.ts` listing | yes, chapter 3.15 |

## R5 — The repair path the whole resume decision rests on has no test

**This is the chapter's most important finding and it is a gap rather than a fact.**

The spec chose Slack's model: resume replays by sequence, and a client repairs a stale message
by re-reading history. That works only because the REST history endpoint returns tombstones
and edited text unchanged. Verified **by inspection of the complete path** — `listMessages`
selects `messages.text` with no predicate on it, the service maps rows straight through, and
the response is not validated outbound (`ZodValidationPipe` is on the *query* only).

**No test covers it.** `grep` for a tombstone in the api's message and internal suites returns
nothing; the only planted tombstones in the repository are chapter 3.15's, and they test the
**listing**, not history. Chapter 3.15 wrote its listing test explicitly *"so the day
FR-MSG-08's chapter ships, the count and the preview already agree"* — history was not given
the same treatment.

**So this chapter owes history that test, and owes it BEFORE the writer exists**, for the same
reason 3.15 gave: a test written after the writer proves the writer, and a test written before
it proves the reader was already right.

## R6 — Resume: what the decision costs, stated

An edit to a message **newer** than the client's cursor costs nothing: the backfill reads rows
at reconnect time, so it carries current text by construction. An edit to a message **older**
than the cursor is invisible — the row keeps its sequence number, so no gap appears and the
SDK's gap detector never fires.

The three models, and why Slack's:

- **Slack** — events are not replayed; `conversations.history` returns current state and is
  the documented repair. Relay is already this shape.
- **Matrix** — an edit is a new event and a redaction is a new event, so a sync token catches
  them and the problem does not exist. Unreachable cheaply here: FR-MSG-07 keeps the sequence
  number across an edit, so an edit appends nothing a cursor can find.
- **IMAP CONDSTORE/QRESYNC** — a `MODSEQ` beside the sequence, resynced on "changed since X".
  A second cursor dimension FR-RTM-03 does not describe.

## R7 — FR-WHK-02 needs two more event types, and the spec missed this surface

The clause names eight event types. `OUTBOX_EVENT_TYPES` (`outbox/event.ts:55`) holds
**three** — `message.created`, `channel.member_added`, `channel.member_removed` — and its own
comment says *"FR-WHK-02 names eight event types and one existed before this chapter. These
are the second and third."* Chapter 3.20 added two and emitted their webhooks in the same
chapter, which is the precedent.

**Measured, because a set with a count is a pinned place.** Adding `message.updated` and
`message.deleted` moves at least four:

    outbox/event.ts        OUTBOX_EVENT_TYPES, the array
    outbox/event.ts        the branch the comment says the union "now forces"
    outbox/event.test.ts:144  the exact-set assertion
    outbox/event.test.ts:149  toHaveLength(3)

Chapter 3.22 predicted two pinned places for one close code and found four. **This prediction
is four and will be re-measured**, not carried.

## R8 — The publish lives in the controller, and it is guarded

`messages.controller.ts:199` calls `this.fanout.publish(...)` after the send, behind
`if (!message.duplicate && message.text !== null)`. The service does not publish, and the
comment says why: the gateway publishes for its own path already, so a publish in the service
would put every socket-sent message on the fabric twice.

**An edit and a deletion have only one entry path** — a REST route — so they have no
equivalent double-publish hazard. That asymmetry is worth stating rather than discovering.

## R9 — Sequence numbers, and what an edit must not touch

FR-MSG-07 preserves the sequence number by requirement. Nothing in the platform reassigns one,
and the listing orders by `channels.last_activity_at` rather than by message time — so
FR-015's "an edit must not re-order the listing" holds as long as neither route touches
`last_activity_at`. **That is a thing to not do**, which is harder to test than a thing to do:
the test has to assert a value is unchanged across an operation that had no reason to change
it.

## R10 — A message with no author cannot be authorised against

121,250 senderless rows exist in the lane, every one written before chapter 2.6's fix, and
`backfill.controller.ts:92` already drops them for exactly this reason. An edit or a deletion
authorises against the author; a row with `user_id NULL` has none.

FR-018 refuses both operations on such a row. **The alternative — treating a null author as
"anybody may"** — would make the oldest rows in the system the least protected.

## R11 — Idempotency is the send path's, and this chapter should not inherit it

The send path carries idempotency keys because a retried send must not create a second
message. An edit is naturally idempotent in its effect (the text ends up the same) but **not
in its history**: two identical edits would append two rows to `message_edits`. A deletion is
idempotent by FR-009, which says the second one changes nothing and emits nothing.

**No idempotency key is proposed for either route.** The edit's history duplication is
accepted and stated; adding a key would be a new contract on a route that has no retry
semantics to protect.

## R12 — What this chapter does not discharge

- **FR-MOD-03**, the moderation audit log. A deletion by API key is permitted here and audited
  by a later chapter. Stated in the spec's Out of scope, repeated here because the gap is
  created by this chapter rather than inherited.
- **FR-MOD-04**, compliance erasure, which is where FR-MSG-08's second sentence sends hard
  deletion.
- **Reclaiming hosted media** referenced by a deleted message's attachments.

## R13 — The fabric carries a `Message` and stamps every arrival `message.created` — MEASURED, and it changes the plan

**Found by analysis pass 1, and it fired the plan's own early-warning sign.**

`packages/protocol/src/fanout.ts:18` states the subject's grammar in its own words:
*"the fan-out has always carried a wire frame's payload rather than a shape of its own"* —
that shape is `Message`. `services/gateway/src/fanout.ts:44` types the delivery handler
`(channelId: string, message: Message)`, and `services/gateway/src/session.ts:347` stamps
every arrival:

    send(connection.socket, { type: "message.created", payload: message });

**Two consequences, and the second is fatal to the first plan:**

- An **edit** is a `Message` and could ride `chan:{channel_id}` by shape — but the receiver
  has no way to know it is an update. The kind is not in the payload; it is hardcoded at the
  socket.
- A **deletion is not a `Message` at all.** It has no text, which is the same constraint that
  gave `message.deleted` its own frame payload (R2). It cannot ride `chan:` even in principle.

**CLAUDE.md records the governing rule, reached independently by three chapters:** *"a fabric
owns its subject grammar, and a kind that cannot share a payload type cannot share a
subject."* ADR-19 took `presence:{channel_id}` on that argument, ADR-20 took
`member:{channel_id}` and `member:{env}:{user}`, ADR-21 took `typing:{channel_id}`. Four
grammars, five subject strings:

    chan:{channelId}                presence:{channelId}
    member:{channelId}              typing:{channelId}
    member:{environmentId}:{user}

**So this chapter takes a fifth, and owes ADR-24 in both homes.** The plan said no ADR was
expected and wrote down that if one became necessary the plan was wrong somewhere. It was
wrong here, and the sign worked — which is the argument for writing that sentence rather
than assuming the happy case.

**The typed points, measured rather than carried.** ADR-19's record said three and a
re-derivation found eight over seven places; this is the count for the message fabric alone,
taken now and to be re-taken when the phase runs:

    packages/protocol/src/fanout.ts          1
    services/api/src/fanout/publisher.ts     3
    services/gateway/src/fanout.ts           7
    services/gateway/src/session.ts          4

**The shape the precedent suggests** is one grammar carrying both mutations with a
discriminator in the payload, which is exactly what ADR-20 did for membership —
`membership.changed` carries `change: "added" | "removed"` rather than taking two subjects.
The name is settled in the phase, not here.

## R14 — A THIRD decision already made in code that this chapter makes live

The backfill's truncation flag is computed from rows **read**, not frames **delivered**:
`repository.ts:4835` is `truncated: rows.length > limit`, and
`backfill.controller.ts:64` states the rule in its own comment — *"Truncation is reported as
the READ found it, not as the mapping left it: dropping an unrenderable row does not mean the
client should go page history, and hiding a real cap would."*

So a page of 500 rows containing tombstones returns fewer than 500 frames and still says
`truncated: true`. **That is correct, deliberate, and has never run**, because no writer
existed. The spec listed it as an open edge case; it was answered before the question was
asked.

**This is the third time.** Research R4 found three read paths whose tombstone behaviour was
each decided on purpose and exercised by nothing; R5 found that the one the resume decision
depends on has no test; and this is a fourth behaviour on a fifth code path. The pattern is
the chapter's own subject one level up: **a reader written for a writer that does not exist
yet is right until somebody checks, and nobody has.** Chapter 3.15 was the only one to write
the test anyway, and it said why in the test's own comment.

Cited rather than re-derived, which is the point.

## R15 — FR-019 needs no dispatcher change and no migration, MEASURED

Subscription filtering is a runtime string match. `services/api/src/db/repository.ts` selects
endpoints with `(e.eventTypes as string[]).includes(event.type)` against a JSONB array, and
**nothing in `services/dispatcher/src` reads `event_types` at all** — `grep` returns zero.
There is no enum, no check constraint and no migration.

**So adding `message.updated` and `message.deleted` to `OUTBOX_EVENT_TYPES` is the whole of
the work**, and a customer who already subscribed to either string starts receiving
deliveries the day it ships. Recorded so the phase does not go looking for a dispatcher change
that does not exist.

**One thing this measurement also exposed, and it is not this chapter's to fix.**
`webhooks.service.ts:208`'s `assertEventTypes` checks only that the array is non-empty. A
customer can subscribe to a misspelled event type and receive silence for ever with no error
at create time, while FR-WHK-01 says an endpoint subscribes to *"a selected set of event
types"*. `gaps.md` carries it with an owner.

## R16 — `forbidden` is the wrong code, and the reference entry is what says so

`docs/08-error-reference.md`'s entry for the generic 403 states its own scope: *"The generic
case: where a more specific code exists … that one is sent instead"*, and its client action is
*"nothing the client can retry. This is a change of credential or of permission."*

**Neither clause fits a non-author refusal.** No credential grants authorship and no
permission change makes a message yours, so the published remedy is advice nobody can act on.
`codes.ts` argues against reusing the generic code twice in its own comments — for
`wrong_credential_type` and `wrong_credential_service` — both times on the ground that *"the
response has to say what actually happened"*.

**Found because the task was conditional and the condition was never evaluated.** The
error-reference task read *"for any error code either route introduces"*, and `ProtocolErrorFilter` maps a bare 403 to
the generic code — so leaving the condition unevaluated would have made the protocol decision
by omission. FR-022 now states it.

## R17 — The isolation gauntlet can attack the new routes for real, MEASURED

`services/api/src/isolation/fixtures.ts:66` sends a message per tenant and exposes its id at
`:85`. The comment at `:133` says why: *"A message the member wrote, so a read attack has
something to fail to find."*

**So nothing needs building.** A foreign-id attack on `PATCH …/messages/:messageId` reaches an
id that exists in the other tenant, which is the only version of that attack worth running —
without a seeded row it would 404 because nothing is there, indistinguishable from isolation
holding. That is the strongest form of *a test that passes while proving nothing*, and this
fixture already prevents it.

**What DOES need doing is the declaration**: `targets.itest.ts:39` derives the live route table
from the adapter and compares it with a hand-maintained list of 24 entries, so it goes red on
the build that adds a route. `CLAUDE.md` records that happening five times over two features
and calls it the highest-yield check in the repository. Three tasks now declare the three
routes, each in the phase that adds it, because the failure lands inside that phase.

**And `accepts` is the same authorization fact in a second place.** This chapter 3.23's
`gaps.md` item 4 carries
it — including that analysis pass 6 decided the decorator values and created the second home
in the same breath, six passes after the first home already existed.
