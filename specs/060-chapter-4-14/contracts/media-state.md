# Contracts — chapter 4.14

**Feature**: 060 · **Date**: 2026-09-28

Three surfaces change. Two are wire contracts a customer parses; one is an internal fabric
between gateway instances. Shapes are given as the contract, not as implementation.

---

## 1. The delivery attachment gains a state

**Surface**: every door that serves a message. **The set is derived, not listed** — analysis
pass 2 found a three-item list here and in FR-003 while the code holds at least six
construction sites, including the edit response and resume/backfill.

    {
      "type": "media",
      "media_id": "<uuid>",
      "state": "pending" | "ready" | "rejected"
    }

**Three shapes, three roles** (revised at analysis pass 1, which found this section claiming
there were two):

    attachmentSchema             a sender declares       no state — strict, unchanged
    deliveredAttachmentSchema    the api builds          state REQUIRED — new
    forwardedAttachmentSchema    a reader forwards       both, plus the loose escape arm

`messageSchema.attachments` points at the **delivered** shape. It is the outbound contract, not
a request shape, and one schema was serving both.

**Required on the delivered shape, not optional**, per the precedent `frames.ts:89` states:
*"a caller may send none, and a payload the platform BUILDS must always say."* Required is what
makes the compiler name every construction site.

**Request side is unchanged.** A sender still declares `{type, media_id}`. All three request
doors keep `attachmentSchema`, whose `strictObject` already refuses a `state` a caller tries to
send — no new refusal is written, and a test pins it against a future widening.

**The forwarding reader stays permissive.** A durable envelope written by the previous binary
carries no `state` and must keep parsing; it matches the `attachmentSchema` arm. The delivered
shape goes **ahead of** it in the union so a current value matches a typed arm rather than
degrading to the loose one, and the loose arm stays last for the future arm FR-018d put it there
for.

**Compatibility**: additive on the wire. A client parsing the old shape ignores the new key.

## 2. A new client frame

**Terminology, fixed here and used everywhere in this feature**: the **frame** is the wire
object a client receives; **publishing** is the act; the **transition** is the state change that
causes it. "Event" is not used for any of the three.

**Surface**: WebSocket, delivered to subscribers of a referencing channel.

    {
      "type": "media.updated",
      "payload": {
        "media_id": "<uuid>",
        "channel":  "<uuid>",
        "state":    "ready" | "rejected"
      }
    }

**`state` excludes `pending`** — the frame announces a transition *out of* pending, so the value
can never be `pending`. A three-value enum here would be a state the producer cannot emit.

**No `reason`.** A rejection's cause (`declaration_mismatch`, `scan_failed`) stays off the
channel fabric: it would tell every subscriber that a member's upload failed a virus scan.
FR-MED-06's three refusals are already byte-identical for the same reason (R2).

**No message id.** One object may be attached by several messages in one channel; the client
finds its own by media id. The frame answers *this object changed*, not *this message changed*.

**Delivery guarantee is the platform's existing one for channel frames**: a client that misses
it repairs by re-reading history, where the attachment carries the state. The frame is an
optimisation over a correct floor and must not be the only path to the answer (FR-009).

---

## 3. The revision fabric gains a third arm (internal)

**Surface**: `revision:{channel_id}`, Redis, gateway-to-gateway. Not a customer contract.

    { "kind": "updated", "message": <forwarded message> }      existing
    { "kind": "deleted", "message": <deleted payload> }        existing
    { "kind": "media",   "media_id": …, "channel": …, "state": … }   new

`strictObject` on the new arm, matching both existing arms: a field added on one side of a
rolling deploy fails loudly instead of being dropped.

**Why this subject and not a sixth grammar** — R1. Per-channel SUBSCRIBEs stay at **5** against
ADR-25's bound of **6**; `fanout.ts` already subscribes `chan:` and `revision:` together under
one reference count, calling them *"co-extensive by construction"*.

**What the fabric's name now means.** `revision:{channel_id}` carries *something changed about
what this channel's messages show* — an edit, a deletion, or an attachment resolving. The
subject name is narrower than its contents and stays, because renaming it is a wire change and
a fence-chain change across every chapter that publishes the file. Recorded in the module
rather than left for a reader to infer.

---

## 4. The internal verdict seam gains one field

**Analysis pass 3 replaced this section, which said the seam was unchanged.** Its
request, its response to the worker and its compare-and-set all stay. What changes is one value
the handler needs and never had:

    recordMediaVerdict(db, input)
      before  → { applied, state, objectKey }
      after   → { applied, state, objectKey, environmentId }

`recordMediaVerdict` is module-level on a raw `Db`, outside the tenant-scoped repository,
because its caller is a worker rather than a tenant — and the worker's principal carries
`environmentId: undefined` by design (4.4). **Without this value the fan-out has no tenant to
scope with, and the only alternative is an unscoped read of a shared table**, which
constitution I forbids.

**The wire contract to the worker does not change.** `environmentId` is an internal return
value, not a response field; the worker has no use for it and is not told.

## 5. What a test must be able to assert

| Assertion | Contract it pins |
|---|---|
| Attachment carries state at **every door the derivation found** | §1, FR-003, SC-002 |
| A durable envelope with no `state` parses | §1 permissiveness, FR-018d |
| All **three** request doors refuse a declared `state` | §1 request side |
| `messageSchema` cannot be built without a state | §1, delivered shape required |
| One frame per referencing channel, at N = 0, 1, 2 | §2, FR-004, SC-003 |
| No frame on a duplicate verdict | §4 `applied`, FR-005, SC-005 |
| The scoped fan-out returns nothing for the wrong `environment_id` | §4, constitution I |
| The verdict's return carries `environmentId` | §4, without it FR-004 cannot run |
| No frame carries a rejection reason | §2, FR-010 |
| A non-member of a private referencing channel receives nothing | §2, FR-007, SC-004 |
| A client that receives no frame still reports the right state | §1, FR-009, SC-006 |
