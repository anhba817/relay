# Phase 0 research — chapter 4.14, "Pending, ready, rejected"

**Feature**: 060 · **Date**: 2026-09-28 · **Spec**: [spec.md](./spec.md)

Every number here was measured on the development lane on 2026-09-28 with the stack up
(`RELAY_POSTGRES_PORT=15432 docker compose up -d --wait`, all seven containers healthy
including `clamav`). Where a figure is quoted from an earlier document rather than re-run,
it says so.

---

## R1 — Does `media.updated` take a sixth subject grammar? (`docs/12` §7.4)

### What the question actually is

§7.4 reads as though the policy were open. It is not: **ADR-25 decided it** and left the
arithmetic.

> Consolidate onto a typed envelope when either holds: per-channel SUBSCRIBEs would exceed
> **six**, or a gateway instance's projected subject count exceeds **250,000**, computed as
> `5 × channels + 1 × connected users`.

And ADR-19's rule, restated by ADR-24 and cited by four ADRs: **a kind that cannot share a
payload type cannot share a subject.**

### The per-channel count, counted from the source

`docs/11` measured the law `5 × channels + 1 × connected users`, exact on six rows to 20,000
connections. Counted from the gateway rather than assumed, the five decompose as:

    fanout.ts:181     subscriber.subscribe(chan:{id}, revision:{id})     2   one call, two subjects
    presence.ts:390   subscriber.subscribe(presence:{id})                1
    typing.ts         subscriber.subscribe(typing:{id})                  1
    membership.ts:127 subscriber.subscribe(member:{id})                  1
                                                                         -
                                                                         5   matches docs/11

**The load test was not re-run.** ADR-25's rows stand; this is a source count that agrees with
them, which is weaker evidence and is labelled as such.

### Four candidate shapes, and two die on the platform's own rule

**Option A — a sixth grammar, `media:{channel_id}`.** Per-channel SUBSCRIBEs become **6**.
ADR-25 says consolidate when they *exceed* six, so six is permitted — **and it is the last one
that is.** A seventh trips the bound.

**Option B — widen `chan:{channel_id}`.** Refused by ADR-24 in writing: *"everything on
`chan:{channel_id}` IS a creation — the subject's payload is a `Message` and the kind was never
on the fabric at all."* Unchanged.

**Option D — re-deliver the affected message as `message.updated` on the existing revision
fabric.** No new subject, no new frame, and clients already handle it. FR-002 makes it tempting:
the state is read at query time, so a re-read message carries the new state for free.

**It dies on a field that does not exist.** `messageSchema` is `{id, channel, seq, user, text,
attachments, created_at}` — **there is no `edited_at`**. A client receiving `message.updated`
cannot tell an edit from an attachment resolving, so every verified photo would render as
*"edited"* on a message nobody touched. That is ADR-24's own objection to putting edits on
`chan:` — *the receiver has no way to know* — arriving one level up. Option D is the cheapest
shape and the platform has already rejected its reasoning once.

**Option C — a third arm on `revisionFabricSchema`, on the existing `revision:{channel_id}`
subject.** Per-channel SUBSCRIBEs stay at **5**.

### Why C rather than A

`revisionFabricSchema` is already a `discriminatedUnion("kind", …)` with two arms carrying two
different payload types — `forwardedMessageSchema` and `messageDeletedPayloadSchema`, the second
being *"the one frame that does not carry a message"*. **The precedent for more than one payload
type on one subject is on this exact subject**, and ADR-20 states the test it was admitted under:

> an edit and a deletion are two things that happen to one message, a receiver subscribes to
> both or neither, and two subjects would double the subscription bookkeeping for a distinction
> the payload already makes.

**The subscriber sets are identical.** `fanout.ts`'s own comment calls `chan:` and `revision:`
*"co-extensive by construction"* and subscribes them under one reference count. A connection
that wants a channel's messages wants to know when one of those messages' attachments resolves;
there is no client that wants one and not the other.

**And the threshold is a budget, not a permission.** ADR-25 set six so that *"a seventh grammar
at that ratio does not"* fit. Option A spends the entire remaining headroom on a kind that does
not need it, and hands the next chapter wanting a fabric a refusal this chapter caused.

### Decision

**Option C — a third arm, `kind: "media"`, on `revisionFabricSchema`.** Per-channel SUBSCRIBEs
stay at 5 against ADR-25's bound of 6; projected subjects are unchanged at
`5 × channels + 1 × connected users`, so the 250,000 bound is untouched.

**What it costs, and pass 4 found one item missing from this list.** The existing publisher
assumes every arm carries a message: `publisher.ts:135` derives the subject as
`subjectForChannelRevision(revision.message.channel)` and logs `revision.message.id` on failure.
A media arm has neither. **Reusing a subject means reusing its publisher, and this section priced
the subject without pricing the publisher** — the fix is a discriminated switch over the arms,
which `tsc` will demand but which no task had. That is a real cost of option C and it is smaller
than option A's subscription, so the decision stands.

And the subject is named `revision:` and will carry a thing that is not a message revision. The fabric's contract becomes *"something changed about
what this channel's messages show"* — which covers an edit, a deletion and an attachment
resolving — and that sentence goes in the module, because a name that has quietly widened is
worse than one that has widened on the record. Renaming the subject is not free: it is a wire
change and a fence-chain change across every chapter that publishes the file.

**Alternatives rejected**: A (spends ADR-25's last headroom for no property), B (refused by
ADR-24), D (indistinguishable from an edit — no `edited_at` exists).

**This overturns the spec's working answer**, which was Option A. The spec said research must
confirm it by measurement or record why the rule points elsewhere. The rule points elsewhere.

---

## R2 — Does the event carry the rejection reason?

**Decision: no.** The frame carries the media id and the state.

`rejected_reason` is a closed set of two, `declaration_mismatch` and `scan_failed`, added by
`0018`. Broadcasting it puts *"this member's upload failed a virus scan"* on a channel fabric
that reaches every subscriber.

**The platform has chosen this direction once already and said why.** FR-MED-06's three
refusals — another tenant's object, another user's, and an id nobody has — are byte-identical
*"because a refusal naming the cause reports whether somebody else's object exists."* The same
argument applies with more force here, because the audience is a channel rather than the caller.

The sender is not deprived: the reason is on a door already authorised to them, and FR-MED-09's
rendering is a later chapter's subject.

---

## R3 — One frame per referencing channel, or per referencing message?

**Decision: per channel**, and the lane says the distinction is real rather than theoretical.

    channels per referenced object      1 channel    1,545 objects
                                        2 channels      44 objects

`channelsReferencingMedia` already returns `selectDistinct` over channels, scoped by
`environment_id`. Per message would mean a second query and a different shape for no gain the
client cannot compute: a client rendering per message finds its own messages by media id.

**44 objects at N = 2 is the evidence SC-003 needs.** Forwarding a photo is the ordinary way an
object acquires a second reference (FR-MSG-11, since 3.24), and a fan-out written for N = 1
would be correct on 97% of the lane and wrong on the rest.

---

## R4 — What happens to an event for a tombstoned message? (FR-011)

**Answered by construction, and measured rather than assumed.**

    tombstoned messages                 2,867
    tombstoned WITH attachments             0

FR-MED-10's unlink is already built — `repository.ts:5088` and `:5175`, *"`[]` AND IT STAYS
`[]`"*. A tombstoned message therefore cannot match `channelsReferencingMedia`'s containment
predicate, so it contributes no channel, and the event path and the delivery gate agree
**because they run the same query**.

No code is needed. A test is: the property is invisible in the types and one `UPDATE` that
forgot to clear attachments would break both paths at once.

---

## R5 — The event under-delivers relative to the read rule, and that is the safe direction

FR-MED-08's authorisation is **visibility** (`channelVisibleTo`): a user may read a public
channel's messages without being a member. But real-time delivery goes to
`registry.subscribersOf(channelId)`, and a connection subscribes to a channel when its
**membership** says so (`session.ts:593`).

So subscribers ⊆ authorised readers. A non-member of a public channel is authorised to read the
photo and will **not** receive the transition event.

**That is not a defect and it is not a leak** — the set is narrower, never wider, so FR-007
holds by construction. It is the second reason story 1 is load-bearing: the non-member learns
the state the next time they read history. Recorded so that nobody later "fixes" it by
broadcasting wider, which would be the leak.

---

## R6 — What the event is worth, on this lane

    media objects                       5,403     pending 4,725 · ready 564 · rejected 114
    referenced by at least one message   1,589
      of those, pending                  1,051     would emit an event when verified
      of those, ready                      472     already terminal
      of those, rejected                    66

**4,725 pending against 1,589 referenced** is 4.13's sweep population seen from the other side:
most objects are slots nobody used. FR-006's *"publish nothing, fail nothing"* is therefore the
**common** path, not an edge case, and it is the one a naive implementation gets wrong by
treating an empty channel list as an error.

**538 referenced objects are already terminal.** Every one of them is a case where the event
either already fired or never will, and the client's only correct source is the state on the
attachment. This is R7's subject.

---

## R7 — Why the two halves of FR-MED-07 are both required

FR-MED-06 permits attaching an object in `pending` **or** `ready`. For an object attached when
already terminal, **no transition remains to announce** — the event can never fire, and a client
depending on it holds a placeholder for ever.

The state on the attachment (FR-001, FR-002) is the floor: correct for every object, at every
door, with no event. The event (FR-004) removes the polling.

This is the same shape 4.13 recorded for the upload notice against the sweep: *the sweep is the
mechanism and a notice is an optimisation that must not change any answer.* Here the state is
the mechanism and the event is the optimisation. SC-006 is what holds it — a client that
receives no event at all must still report the right state.

---

## R8 — Where the producer hangs, and the value it does not have

**REVISED BY ANALYSIS PASS 3. The first version of this section was wrong in the sentence that
mattered.** It read: *"`channelsReferencingMedia` is private to the repository. It becomes
reachable for this path — a visibility change on an existing tested query, not a second query."*
It is neither, because the seam has no tenant.

### The seam is right and it is missing one value

`POST /internal/media/:mediaId/verdict` (`internal/media.controller.ts:115`) is a good place to
hang a producer in every respect but one:

- `recordMediaVerdict` already distinguishes *a transition happened* from *a verdict arrived*,
  and returns `applied`;
- the two refusal paths — 404 for no such object, 422 for an already-`rejected` one — both
  return before it;
- there is exactly one site before `return` where a publish belongs.

**What it does not have is the object's tenant.**

    recordMediaVerdict(db, input)
      → { applied: boolean, state: string | null, objectKey: string | null }

A module-level function taking a raw `Db`, deliberately outside the tenant-scoped repository,
because the caller is a worker and not a tenant. Its `.returning({ state, objectKey })` carries
**no `environment_id`**. And the worker's principal carries `environmentId: undefined` **by
design** — 4.4 established that and its own comment says the absence is what stops a platform
principal being usable where a tenant is expected.

`channelsReferencingMedia` is a **private instance method** scoped by `this.environmentId`. There
is no environment to construct a repository with.

### What this costs, and the one option that is not available

**Two changes, not one:**

1. `recordMediaVerdict` returns `environment_id` alongside `state` and `objectKey` — a change to
   a function 4.13 shipped, to its return type, and to its tests.
2. The fan-out gets a scoped entry point taking `(db, environmentId, mediaId)`, beside
   `recordMediaVerdict` and in the same module-level style, reusing the existing query body.

**The option that is not available is dropping the scope.** `media_id` is a primary key, so an
unscoped lookup would return the right rows — and it would be a query reading a shared table
with no tenant predicate, which constitution I forbids in the data-access layer and which
`check-lane-scope.py` exists to find. The plan's constitution table promises *"no new query, so
no second place to forget the predicate"*; carrying the environment from the row is what keeps
that true.

### Why the environment is the right value to carry rather than re-read

The row is already being written. Adding one column to a `RETURNING` list costs nothing and
happens inside the statement that decided the transition. Re-reading the object afterwards to
learn its tenant would be a second statement that can disagree with the first — and the first is
a compare-and-set whose whole point is that nothing else moved.

## Summary of decisions

| | Decision | Overturns the spec? |
|---|---|---|
| R1 | Third arm `kind: "media"` on `revisionFabricSchema`; no sixth grammar. **Pass 4 added the publisher's per-arm cost, which this row first omitted** | **Yes** — spec assumed Option A |
| R2 | Frame carries state, not the rejection reason | No |
| R3 | One frame per referencing channel | No |
| R4 | Tombstone needs no code; assert the property | Sharpens FR-011 |
| R5 | Event reaches subscribers ⊆ authorised; safe direction, recorded | New |
| R6 | N = 0 is the common case (4,725 of 5,403) | New |
| R7 | Both halves required; 538 lane objects prove it | Confirms |
| R8 | Producer hangs on the verdict's compare-and-set — **and `recordMediaVerdict` must return `environment_id`, which pass 3 found missing** | **Yes** — R8's first version said a visibility change would do |

**Unresolved: none.** No `NEEDS CLARIFICATION` remains.
