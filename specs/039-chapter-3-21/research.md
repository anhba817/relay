# Research — chapter 3.21, the typing indicator

*Every entry is a question asked of the repository with a yes-or-no answer, and the
command that answered it. Two of the brief's premises were false and are R1 and R2.*

---

## R1 — Can typing ride `chan:{channel_id}`? **No, and there are SEVEN typed points, not
three.**

The brief said typing is the one remaining kind that needs no new grammar. ADR-19 refused
`chan:` for presence because the message path is typed to messages at three points. **That
count is wrong, this entry's first version said four, and running its own verification
command in analysis pass 4 returned eight lines covering seven places:**

    services/gateway/src/fanout.ts:44   onDelivery(handler: (channelId, message: Message) => void)
    services/gateway/src/fanout.ts:47   publish(message: Message): Promise<void>
    services/gateway/src/fanout.ts:62   let deliver: (channelId, message: Message) => void
    services/gateway/src/fanout.ts:80   messageCreatedSchema.shape.payload.safeParse(parsed)
    services/gateway/src/session.ts:223 send(socket, { type: "message.created", … })
    services/gateway/src/session.ts:896 the same literal, in the resume flush
    services/gateway/src/session.ts:912 the same literal again

ADR-19 named three. This entry named four. **Nobody re-derived it until a task said to run
the grep** — and `fanout.ts:62`'s `deliver` type and two more literal `message.created`
sends in `session.ts` had been sitting there the whole time.

The argument is not weakened by the correction. It is stronger: **seven places to widen
rather than three.** Carrying a second kind on `chan:` means changing a type in four places,
loosening a parse that currently rejects everything that is not a message, and editing the
highest-volume path in the system — fenced by ten chapters — to serve the lowest-volume
traffic on it.

**Decision: a fourth subject grammar.** `chan:`, `presence:{channel_id}`,
`member:{channel_id}` + `member:{env}:{user}`, and now typing's.

**What is new is not the decision but its status.** Three consecutive chapters have now
reached it from three different starting points, which makes it the pattern rather than a
judgement call: **a fabric owns its subject grammar, and a kind that cannot share a
payload type cannot share a subject.** The chapter should say that, because a reader
watching a fourth grammar arrive deserves the rule rather than a fourth argument.

**Alternative rejected: an enveloped payload on `chan:`.** Same as ADR-19's — it puts a
discriminated-union parse on every message every instance receives, and during a rolling
deploy an old instance logs `fanout.invalid_payload` for every keystroke on every channel.
Worse here than for presence, because typing is higher frequency than presence by orders
of magnitude.

---

## R2 — Can a client tell the server it is typing? **No. Not one frame in the protocol
lets it.**

    services/gateway/src/session.ts:948
    if (frame.data.type !== "message.send") {
      sendError(socket, "unknown_frame_type", `clients may not send ${frame.data.type}`);
      socket.close(4002, CLOSE_CODES[4002]);
    }

`message.send` is the only inbound frame, and chapter 3.12's gauntlet states it as a row —
*"the only frame a client may utter (session.ts)"* — while classifying `typing` as
**outbound**: *"server-fanned; a client claiming one could type as anybody."*

**This is the chapter's real size.** It is the first to open a second inbound frame, and
the inbound seam is where a protocol is attacked. Everything the gauntlet asserts about
direction has to keep holding for the other nine types while one moves.

**Decision: a NEW inbound frame type, not the existing `typing` made bidirectional.** A
bidirectional `typing` carries `{ channel, user }`, so a client could name a user — which
is precisely the attack the gauntlet's row describes. The inbound frame carries a channel
and nothing else; the identity comes from the connection, the way chapter 3.17 made the
send path resolve its sender.

---

## R3 — Where does the expiry live? **In the receiving client, and the protocol decided
it before this chapter arrived.**

    packages/protocol/src/frames.ts:96
    export const typingSchema = z.strictObject({
      type: z.literal("typing"),
      payload: z.strictObject({ channel: …, user: … }),
    });

Two fields. No `state`, no `until`, no `expires_at`. **There is no frame for "X stopped
typing"** and there never has been. The three options the brief asked to be named and
priced are therefore not equally available:

    a Redis key with a TTL      the server would know when it lapsed and could publish
                                nothing about it — there is no frame to send. The key
                                would exist to answer a question nobody can ask.
    a gateway-local timer       same, plus it is per instance, so two instances hold two
                                answers to one question and neither can announce either.
    the receiving client        the only one the published frame supports: five seconds
                                from the last frame for that (channel, user), cleared
                                locally.

**Decision: the client's timer. Cost: zero Redis keys, zero server timers, zero state.**
That is what makes FR-RTM-08's *"shall not be persisted"* true by construction rather than
by discipline.

**And it makes the renewal interval the only number this chapter has to choose**, because
the expiry is fixed at five seconds by the clause.

**Reversing this means editing `typingSchema`**, which chapters 3.19 and 3.20 both refused
for a stated reason: the frame a client parses is what chapter 1.3 published and
`frames.test.ts` asserts. Recorded as reversible rather than closed.

---

## R4 — What breaks when the union gains an eleventh member?

    services/gateway/src/isolation.itest.ts
    it("derives all ten members from the union itself", …)  expect(members.length).toBe(10)
    it("classifies every member exactly once", …)
    it("names no frame the union does not have", …)

**The gauntlet fails on the build that adds a frame type**, by construction, the way the
api's derived target list fails on the build that adds a route. That check has fired six
times in three features and is the highest-yield instrument in the repository.

So the eleventh type is a decision three tests force somebody to make: the count moves to
11, the new type gets a DIRECTIONS row with a direction and a reason, and the sample
builder at `isolation.itest.ts:759` gains a case.

**This is a feature of the plan, not a cost.** Nothing else in the tree would notice.

---

## R5 — Can typing reuse the existing token buckets? **No, and the first version of this
entry said yes.**

    services/gateway/src/limits.ts:83   operation: "connect" | "send"
    services/gateway/src/limits.ts:89   const WINDOW_MS = 60_000
    services/gateway/src/limits.ts:115  `rl:${environmentId}:${operation}:${windowStart}`

This entry originally read *"the key grammar already carries the operation, so a third
bucket needs no schema change and no new Redis shape"*, and recommended a third
`"typing"` operation. **That is true of the grammar and false of the semantics**, which
analysis pass 1 found by reading two more lines of the same file.

The bucket is keyed on the **environment** and counts within a **60-second** window. The
requirement is at most one publish per **2 seconds** per **connection and channel**. Those
are three mismatches, and each is fatal on its own:

    scope    per tenant       vs   per connection — one tenant's 10,000 users would share
                                   one typing budget, and one chatty user would silence
                                   the rest
    window   60 s             vs   2 s — "N per minute" cannot express "one per 2 s"
    subject  no channel       vs   per channel — typing in two channels is two indicators

**Decision: a gateway-held debounce, and no Redis at all.** A `Map` keyed by
(connection, channel) holding the last publish time. The gateway drops a signal that
arrives inside the interval.

**And the third bucket is not built, which is the simplification.** A per-environment
ceiling would bound a rate the debounce already bounds: the gateway enforces the interval
itself, so a hostile client cannot exceed it by trying. What is left unbounded is the
number of connections, and **that is FR-RTM-09's cap — chapter 3.22 — not this chapter's.**

**The refusal is silence, and now it logs nothing either.** A refused connect is a 429 with
`Retry-After`; a refused send is an error frame. A signal inside the interval is dropped
with no frame and no log line, because one line per keystroke over the interval is exactly
the unbounded output NFR-OBS-01 exists to prevent.

## R6 — What is the renewal interval, and what does it cost?

The expiry is five seconds and fixed by FR-RTM-08. The renewal interval is this chapter's
only free number, and it is bounded on both sides:

    too long   > 5 s   the indicator flickers: it expires before the renewal arrives
    too short  → 1/keystroke, which is the publish rate this requirement exists to bound

**Decision: renew at most once every 2 seconds per (connection, channel).**

    5 s expiry / 2 s renewal = 2.5 renewals per expiry window — two chances to arrive
                               before the indicator lapses, so one dropped publish does
                               not flicker
    10,000 connections per instance, all typing continuously
                             = 5,000 publishes per second per instance worst case
    realistically             typing is bursty and per channel; the ceiling is the number
                               that matters and it is stated rather than hoped

**The margin is the point, and chapter 3.19 is why.** Its grace check armed at exactly
`graceMs` put two deadlines on one instant reached by two clocks and stranded a user online
for ever. 2 s against 5 s is not a round number chosen for tidiness; it is 2.5 chances,
and a single lost publish costs nothing visible.

**The client enforces it and the server enforces it too.** A well-behaved client sends one
signal per interval; the server's bucket makes a badly-behaved one cheap rather than
trusted.

---

## R7 — Does a typing frame belong in the resume buffer?

No, and chapter 3.20 already built the argument for a frame with no sequence. Its
`deliverMembership` consults neither `connection.phase` nor `connection.marks`, and its
comment states why: a frame carrying no sequence can neither duplicate a backfilled row nor
leave a gap.

Typing is the stronger case. A membership change is still true when it arrives late; **a
typing indicator replayed after a reconnect is a claim about the present that was true five
seconds ago.** It must be dropped rather than buffered.

`flushable(buffer, marks)` filters on `frame.seq` and nothing else, which is the reader
chapter 3.20 found the hard way. A typing frame that entered the buffer would flush.

---

## R8 — Which published prose does this chapter contradict?

**THE FIRST VERSION OF THIS ENTRY SEARCHED THE WRONG TREE, AND ANALYSIS PASS 3 FOUND WHAT
IT MISSED.** It said "checked with `grep` against both locales", meaning
`relay-tutorial/app/(en)` and `(vi)`, and found three claims in chapter prose. It never
looked at `docs/`.

**`docs/` is where the PRODUCT's claims live. The tutorial is where a chapter's NARRATIVE
claims live.** A customer reads the first one. Chapter 3.20 found this same class in
ADR-07's deep dive — also `docs/` — and this entry still did not include the directory.

The search space is both trees:

    relay-tutorial/app/(en)/**  and  (vi)/**      chapter narrative
    docs/*.md                                     the product's own documents

**Four claims, eight fragments.** All extracted with `grep` and verified present before
being written here.

    1  docs/08-error-reference.md — THE CUSTOMER-FACING ONE, and the sharpest
       :264 "`message.send` is the only inbound frame; every other member of the
             frame union is server-to-client"
       :272 "**What to do:** send `message.send`. Do not send events; receive them."

       This is the reference entry for `unknown_frame_type` — **the error code this
       chapter's own seam produces.** After this chapter a customer refused for a
       typing frame would read documentation telling them the wrong thing, in the
       document written to explain that refusal.

       `check:errors` cannot see it: that checker asserts 17 codes each with a cause
       and a client action, which is structure. Whether the prose is TRUE is not a
       property it checks.

       This file is in `sync-docs.sh`'s published list, so the correction mirrors.

    2  chapter 3.19, on the six kinds
       en  "typing" named as a kind still without a producer
       vi  the same sentence

    3  chapter 3.20's "what this chapter does not do"
       en  "the one kind that could genuinely reuse `chan:{channel_id}` rather than
            needing a fourth grammar"
       vi  the same

    4  chapter 3.20's ForwardRef
       en  "the first that can reuse a grammar rather than adding one"
       vi  the same

**Claims 3 and 4 are mine, written one chapter ago, and they are wrong.** A ForwardRef is a
prediction, and this project has now published two in one chapter that the next chapter
falsified. The correction is not "3.20 was careless" — it is that **a ForwardRef should
describe what the next chapter must decide, not what it will conclude.**

**Two things came back clean.** `packages/outsider` only reads frames and sends none, so a
new inbound type does not touch the sealed client. And no document counts the subject
grammars — ADR-19 and ADR-20 each name their own without asserting a total — so a fourth
breaks no published count.

## R9 — What does the lane cost, and where does this chapter land?

    two twenty-run batteries    17/20 and 16/20 green
    lane mean                   228.50 / 228.77 s   budget 240 — 11.2 s headroom
    gateway package             45.50 / 45.48 s     the pacesetter is presence.itest.ts
    43 files, 701 tests

**There is no room for a tenth gateway integration file that spawns its own api.** Seven
of nine already do, chapter 3.20 added the seventh and recorded it as making 3.19's item 15
worse, and five of the seven battery failures across forty runs were a gateway api fixture
failing to come up.

**So this chapter's integration tests go in an existing file or share an api.** The
decision belongs in planning; the constraint is recorded here.

---

## R10 — What do the clauses actually say?

Read rather than enumerated, which is this project's second-highest-yield mechanism.

    FR-RTM-08  "Typing indicators shall expire automatically after 5 seconds without
                renewal and shall not be persisted."

Two obligations, and **neither is about delivery**. The clause says nothing about who may
signal, nothing about scope, nothing about rate. Those come from FR-RTM-05 (the kind
exists), FR-RTM-01 (members of a channel receive its events) and FR-RTL-01 (operations are
counted). A chapter that read only FR-RTM-08 would build an expiry and no feature.

    FR-RTM-05  names six kinds. After this chapter four have producers:
               message.created (2.6), membership.changed (3.20), presence.changed (3.19),
               typing (this chapter). message.updated and message.deleted wait on
               FR-MSG-07 and FR-MSG-08 — chapter 3.23.

**No SRS clause changes.** Verified by reading; to be verified again by `git diff` at the
end, because expected is not verified.
