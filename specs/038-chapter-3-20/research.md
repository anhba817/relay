# Research — chapter 3.20, the membership that changed under a live socket

*Every entry is a question with a yes-or-no or a number for an answer. Where a command
was run, its output is here rather than its conclusion.*

**Line numbers describe the tree at the fence predecessor `d38f415`.** This feature will
edit `services/gateway/src/session.ts` and `services/api/src/db/repository.ts`, so numbers
in both move during implementation. Tasks anchor on symbols.

---

## R1 — Can a membership change ride either fabric this system already has?

**No, and the reason is the direction it is addressed in.**

    chan:{channel_id}       carries messages to a channel's subscribers   (2.6, ADR-07)
    presence:{channel_id}   carries transitions to the same audience      (3.19, ADR-19)

Both assume the receiving instance is **already subscribed to the channel**. Checked
against the two cases:

    a REMOVAL   the affected user is a member, so their instance IS subscribed  -> reachable
    an ADDITION the affected user is not a member yet, so their instance is NOT -> unreachable

**The addition is the case that decides this.** A gateway holding Tuan's socket is not
subscribed to `#night-shift` before he joins it, so nothing published on any subject
derived from that channel can reach him. This is the first event in the system whose
recipient is a **principal** rather than a channel.

**Decision: two subject shapes, and the asymmetry is topology rather than taste.**

    member:{channel_id}      one publish reaches every instance holding a member —
                             which for a REMOVAL includes the removed user's own
    member:{env}:{user}      one publish reaches the instances holding that user,
                             which is the only way to reach a NEW member

A removal needs only the first: the channel-addressed publish reaches Mai's instance and
Tuan's instance in one go, and Tuan's instance recognises its own user in the payload,
delivers the frame, then unsubscribes him. An addition needs both — the channel half tells
the existing members, the user half tells and subscribes the new one.

**Rejected: publish to every remaining member's user-subject.** It removes the
channel-addressed grammar and replaces one publish with one per member. A 1,000-member
channel (FR-CHN-07's ceiling) would cost 1,000 publishes for one removal, which is the
option that gets worse exactly where the product is trying to grow.

**Rejected: reuse `presence:{channel_id}`.** It is typed to `presenceFabricSchema`, a
`strictObject` of three fields, and chapter 3.19 chose that strictness deliberately so a
field added on one side of a rolling deploy fails loudly on the other. Widening it would
spend that.

**The declared cost** is one more subscription per channel per instance — the third — plus
one per locally-connected user. **Measure it in phase 0 the way chapter 3.19 did**, with
`CONFIG RESETSTAT` and `INFO commandstats`, and record the number rather than the
adjective. 3.19's reading for two instances over three channels was
`cmdstat_subscribe calls=12`; this feature's prediction is 18 plus one per connected user,
and a prediction is not a measurement.

---

## R2 — Does constitution II forbid publishing this after commit?

**Yes, as the design stood before this question was asked — and this is the finding that
changes the shape.**

Constitution II: *"State changes and their events MUST commit atomically via the
transactional outbox (SAD ADR-06). **Publish-after-commit without the outbox is
forbidden**: it silently drops events and makes metering drift undetectable."*

Chapter 3.18 publishes `message.created` to Redis after the commit, and that is not a
violation, because the same transaction already wrote the outbox row —
`services/api/src/db/repository.ts:4045`, inside the insert branch, with its own comment:
*"no message without its event, no event without its message."* The Redis publish is a
**second, lossy delivery of something the outbox already durably recorded**, which is what
constitution IV permits.

**A membership write records nothing.** One grep over `channels.service.ts` for `outbox`
returns nothing at all; the only `tx.insert(outbox)` in the repository is the message one.
So a Redis publish after a membership commit would be an event with no durable record —
precisely the case constitution II names.

**Decision: the membership write gains an outbox row, in its own transaction, and the
Redis publish is the lossy live path beside it.** That is the message path's shape exactly,
already built and already taught, which is the strongest argument available for it.

**And FR-WHK-02 already spells the event types.** Read, not assumed:

    FR-WHK-02 | The system shall emit at minimum: `message.created`, `message.updated`,
                `message.deleted`, `channel.created`, `channel.member_added`,
                `channel.member_removed`, `user.connected`, `user.disconnected`. | P2

Eight names; one exists. `channel.member_added` and `channel.member_removed` are two of the
seven missing, and they are the two this chapter's state change owes. So the outbox row is
not an invention to satisfy a principle — it is a requirement that was already written
down, at P2, waiting for the write that would produce it.

**What this chapter does NOT do**, and the distinction has to survive into the tasks: it
writes the outbox rows and stops there. It does not build webhook subscription for the new
types, does not extend the dashboard, and does not claim FR-WHK-02 is met — five of its
eight names would still be missing. The rows are written because constitution II requires
them for the publish this chapter *does* make, and their existence is what makes the
webhook chapter a wiring job rather than a re-plumbing job.

**One code fact this costs.** `services/api/src/outbox/event.ts:29` types the envelope's
`type` as the literal `"message.created"`, not a union. Adding two event types widens that
literal, and the widening is visible to every consumer that narrows on it — which is the
kind of change a typecheck catches and an integration lane does not.

---

## R3 — What preserves the recovery property constitution IV demands?

**Nothing yet, and this is the one honest gap in the design.**

Constitution IV: *"The live fan-out fabric is permitted to be lossy (at-most-once)
precisely because durability and resume live in PostgreSQL sequences and cursors (SAD
ADR-07). **Any new delivery mechanism MUST preserve this recovery property.**"*

For a message the recovery is the resume cursor: a dropped `message.created` is redelivered
on the next reconnect because the client asks for everything past its sequence. **A
revocation has no cursor.** A dropped one leaves a removed user receiving until they
reconnect, which is FR-RTM-10's exact prohibition, and nothing in the system would notice.

Three candidates, with what each costs:

**(a) A periodic re-read in the gateway.** Each connection's channel set is refreshed from
the api on an interval. Correct without any fabric at all, and it is the only option whose
worst case is bounded by a number the design chooses. The cost is request volume:
NFR-SCL-01 budgets 10,000 connections per instance, so a 60-second interval is 167
requests per second per instance against `/internal/…` — and a 5-second interval, which is
what FR-RTM-10's window would demand of a re-read *alone*, is 2,000.

**(b) A JetStream consumer in the gateway.** At-least-once, and the outbox row from R2
already exists to feed it. Rejected on ADR-07's own words — *"a clean mapping — gateway to
Redis, api and workers to NATS"* — and on constitution VII: it makes the gateway a second
kind of consumer for one event type.

**(c) Accept the loss and record it.** FR-014a permits this outcome explicitly and says
what it costs: FR-RTM-10 is then met on the happy path and unmet under fabric loss, written
down as such rather than a clause narrowed until it passes. Chapter 3.18 faced the same
temptation with this same clause — *"a specification edited until it matches the code has
stopped being a specification"* — and refused it.

**Decision: (a) as a backstop, not as the mechanism.** The Redis publish is the fast path
and meets the five seconds; the re-read exists so that a dropped publish is corrected by
something other than the user's decision to reconnect. **The interval is therefore not
FR-RTM-10's five seconds** — it bounds the damage from a rare drop, not the ordinary case,
and picking it is a measurement task rather than a guess. The number goes in the chapter
with its arithmetic beside it.

**This is the entry most likely to be wrong, and it is wrong in a specific way if it is.**
The re-read costs a request per connection per interval and the lane cannot see it: chapter
3.19's largest membership set was five channels and its largest instance count was two.
NFR-SCL-01 is undischarged and stays undischarged.

---

## R4 — Is there a contract for the re-read, or does one have to be invented?

**There is one, it has been exported for eighteen chapters, and nothing parses it.**

`packages/protocol/src/internal.ts:121`:

    /** api → gateway: the channels this user may hear (FR-RTM-01). */
    export const internalMembershipsResponseSchema = z.strictObject({
      channel_ids: z.array(z.string().min(1)),
    });

Eleven lines below, the schema that replaced it says so: *"This replaces the memberships
response above rather than joining it."* Chapter 3.2 moved identity and memberships into
one answer at connect and left this one behind.

Checked rather than assumed:

    grep for internalMembershipsResponseSchema outside its own file   nothing parses it
    grep for "/internal/memberships" in the api                       no route serves it
    services/api/src/tenancy/signup.itest.ts:280                      POSTs the path and
                                                                      asserts it is not 200

**The negative fixture is real but narrower than it looks, and the difference matters.**
`services/api/src/tenancy/signup.itest.ts:280` — *"exposes provisioning nowhere but the signup
path"* — **POSTs** to `/internal/memberships` with no credential and asserts `status !== 200` and
that the body does not contain `organisation`. A GET-only route answers that POST with a 404 and
the assertion still holds.

So reviving the route as a GET breaks nothing, and the first draft of this entry said it would.
What *would* break it is registering the handler for `ALL` or adding a POST twin, and what would
break its intent is a route that answers 200 to an unauthenticated caller. **Check it in the pass
that writes the task, by reading the assertion rather than the path** — the two are not the same
evidence, which is the whole reason this correction is here.

**Decision: revive it rather than delete it, and fix the fixture in the same change.** The
re-read in R3 needs exactly this shape — a user's channel ids and nothing else — and
inventing a second contract for it while this one sits unused would be the habit chapter
3.8 named. FR-017 permits either answer and asks for the reason; this is the reason.

**The alternative, deleting it, is genuinely cheaper if R3 lands on (c).** If no backstop
ships, nothing needs this contract and it should go. **So R3 and R4 must be decided
together**, and a task list that orders them the other way round has already chosen.

---

## R5 — Where does the five seconds actually go?

FR-RTM-10 says *"effective within 5 seconds of the membership change"*, and the spec's own
assumption is that the clock starts at the write rather than at the publish. The budget
against the mechanism in R1 and R2:

    the transaction commits                          t0
    the api publishes on member:{channel_id}         t0 + one Redis round trip
    the subscribing instance receives                + pub/sub latency
    it unsubscribes chan: and presence: for the user + two Redis round trips
    registry.subscribersOf stops returning them      immediate, in process

Every term is a local round trip and the total is milliseconds, not seconds. **The five
seconds is not a latency budget here; it is the margin the clause leaves for a mechanism
that does not exist yet.** Worth stating in the chapter, because a reader who sees five
seconds in a clause and milliseconds in a test will otherwise assume one of them is wrong.

**The one term that is not milliseconds is the backstop.** If R3's interval is 60 seconds,
then the *worst* case — a dropped publish — is 60 seconds and the clause is missed. That is
the honest reading of FR-014a and it belongs in the chapter rather than in a footnote.

---

## R6 — What has to change in `session.ts`, and what breaks if it does?

The gateway's session layer holds **four** things this feature must mutate while a socket is
open, and all four are read on the delivery path:

    connection.channelIds        a Set, built once at connect from POST /internal/session
    fanout.subscribe/unsubscribe reference-counted per channel, run once at open and close
    presence.subscribe/unsubscribe   the same, added in 3.19
    connection.buffer            messages the fabric delivered during a backfill, flushed by
                                 `flushable(buffer, marks)` — which filters on `frame.seq`
                                 and NOT on membership (FR-029, FR-030)

**This entry said "three" until analysis pass 12, and the omission is the most instructive thing
in this file.** The buffer is not missing because anyone overlooked a line; it is missing because
of the question this entry asks. *"What does the session layer hold that a membership design must
mutate?"* returns exactly the three above — a channel set and two subscription counters — because
those are what a membership design thinks about. **The buffer belongs to the message path**, so
the question as posed could not reach it, and the conclusion two lines below made the blind spot
sound like a finding: *"This is the first change to `connection.channelIds` after the connection
exists."* True, and it framed the whole problem around one Set.

The question that does reach it is *"what else reads or writes this connection's state?"* Pass 3
got there by a different road — reading the edge-case list, which happened to contain
*"a user removed from a channel during their own resume backfill"* — and it cost a CRITICAL to
find that way. **Ask the second question when enumerating state, not the first.**

**This is the first change to `connection.channelIds` after the connection exists.** Every
reader of it assumes it is immutable for the connection's lifetime; chapter 3.19's own
comment on the close handler says the ordering there *"now carries three ordering
constraints, not one"*, and this feature adds a fourth mutation point in the middle of the
connection's life.

**The reference counting is the sharp edge.** `fanout.subscribe` and `presence.subscribe`
count per channel per instance, so two local members of one channel share one Redis
subscription. Removing one member must decrement, not unsubscribe — and a decrement that
runs twice for one removal unsubscribes a channel another member is still reading. The
close path already gets this right; the new path is a second caller of the same counters
and the first one that can be driven from outside the connection's own lifecycle.

**What a test must therefore assert**, and it is not the obvious one: after a removal, a
**second** local member of the same channel still receives that channel's messages. A test
that only checks the removed user is satisfied by an implementation that unsubscribes the
channel outright.

---

## R7 — Does the isolation gauntlet already cover the new frame?

**Yes for the frame, no for the route.** `services/gateway/src/isolation.itest.ts:728`
carries `["membership.changed", "outbound", "membership is written through the api, never
the socket"]`, and that row has been green since chapter 3.12 against a system in which
nothing produced one — the same shape chapter 3.19 found for `presence.changed`. **A test
can be green about a capability that does not exist**, and this feature makes the row mean
something for the first time.

The api-side gauntlet derives its target list from the running router, so new routes are
picked up automatically. **This feature adds no route** if R4 lands on reviving
`/internal/memberships` — internal endpoints are not on the public target list — which is
worth checking in the pass that writes the task rather than at close-out. Chapter 3.19's
own record: *"the derived target list fails on the build that adds a route"*, five times
over two features, and it is still the highest-yield check in the repository.

---

## R8 — Which published prose does this design contradict?

Read the chapters rather than grepping the identifiers, because chapter 3.19's four
findings were all sentences and none contained an id that would have surfaced them.

**FOUR claims, eight fragments — and the list said five and ten until analysis pass 6 went
looking for the Vietnamese and could not find two of them.**

**Every fragment below was extracted from the file, in both locales, and verified against
whitespace-collapsed text.** That is not pedantry: two entries in the first draft of this list
quoted wording chapter 3.19 had already deleted, so a checker built from it would have carried
four fragments that could never match and reported green on them from the first run.

    1  chapter 3.18, BODY PROSE — not a forward reference, and a claim of IMPOSSIBILITY
       en :634  "Nothing in between re-reads membership, and no code path could"
       vi :638  "Không gì ở giữa đọc lại membership, và không đường code nào có thể"
       THIS CHAPTER BUILDS THAT CODE PATH. The measurement around it stays true and the
       impossibility does not. A reader meets it as settled architecture mid-argument, and
       no forward-reference sweep would have found it — pass 4 found it by reading.

    3  chapter 3.18's ForwardRef, IN THE WORDING CHAPTER 3.19 LEFT THERE
       en :1602 "so the clause stays open rather than being fixed on the way through"
       vi :1617 "nên điều khoản vẫn để ngỏ thay vì được sửa tiện đường"
       3.19 rewrote this passage when it corrected 3.18's premise. This chapter closes the
       clause, so the replacement is false in its turn.

    4  chapter 3.19's ForwardRef
       en       "a re-read the session layer owes"
       vi :2711 "một lần đọc lại mà session layer còn nợ"
       This chapter builds it, so the tense changes.

    5  chapter 3.19's Trap — the artefact class that survived fifteen passes in chapter 3.17
       en :1009 "does not appear online to that channel's members until they reconnect"
       vi :1008 "sẽ không hiện online với thành viên của channel đó cho tới khi họ kết nối lại"
       This chapter makes it false. The English wraps a source line; the checker collapses
       whitespace before comparing, which was checked rather than assumed.

**Claim 2 was dropped, and why is the useful part.** The first draft listed chapter 2.6's
*"presence and typing will reuse this exact pub/sub plumbing"*. That sentence has not existed
since chapter 3.19 corrected it. What stands there now —

> *"presence ends up with a subject grammar of its own **beside** this one rather than inside
> it… Typing's half of this promise is still open."*

— is **not contradicted by this chapter at all.** A third grammar makes none of it false, and
typing is still unbuilt. It was on the list because the list was written from what those
chapters used to say.

**The general rule this produces**: a contradicted-claim list is a claim about the tree like any
other. Extract it with `grep`, in both locales, against the collapsed text the checker will use —
never from memory of an earlier version.

**Checked and cleared in the same pass**, so a later one does not re-ask:
`services/gateway/src/session.ts:693` says *"The limit is the one this socket was born with,
not one re-read per frame… A policy changed mid-connection reaches the client when it
reconnects"*. That is scoped to `connection.sendLimit` — adjacent to this chapter's subject
and not contradicted by it.

---

## R9 — What does the lane cost, and what is the headroom?

Chapter 3.19 closed at **228.18 s mean, stdev 1.41, against a 240 s budget** over eighteen
green runs — 11.8 s of headroom. The per-package shape:

    api          102.21 s   stdev 0.15
    dispatcher    72.65 s   stdev 1.13
    gateway       45.09 s   stdev 0.54    <- and 45.09 IS presence.itest.ts

**This feature's tests land in the gateway package, which is the one with a known
contention problem.** Chapter 3.19's `gaps.md` item 17: six of the gateway's eight
integration files each spawn their own api, vitest runs files in parallel, and run 10 of
its battery failed when one api boot exceeded a 90-second hook timeout. **A seventh
spawning file makes that worse**, and this feature will want one.

**Decision, corrected in analysis pass 1: the new file spawns the seventh api, and says so.**
The first draft said it would "share the api fixture rather than spawning a seventh" — and
**there is no fixture to share.** Six files spawn an api and each carries its own helper;
`presence.itest.ts` shares one *within* its file, across seven describes, worth 21 s. Building
the cross-file version is item 17's actual fix and a job of its own.

So this feature makes item 17 **worse**, and the alternative was worse still: putting the
chapter's headline tests in `session.itest.ts` avoids the spawn and lands them in a file no
chapter fences, which is the defect chapter 3.18 was criticised for. The seventh spawn is paid,
recorded, and the fix given an owner.

**And the wall-clock model in the first draft was wrong too.** The package's clock is
`max(file)`, not the sum — 28 cores, 8 files, all concurrent, which is why the package measured
45.09 s where `presence.itest.ts` alone measured 45.2 s. A ninth file under 45 s costs the lane
almost nothing; the cost is contention, not duration. The budget is 40 s and it is checked after
US1, not at close-out.

---

## R10 — Does anything here need an SRS clause change?

**No clause, and the appendix needs checking rather than assuming.**

    FR-RTM-05   already requires the membership-change event
    FR-RTM-10   already requires the five-second revocation
    FR-RTM-01   already requires delivery for every channel of which the user is a member
    FR-WHK-02   already names channel.member_added and channel.member_removed
    NFR-OBS-01  already requires structured observability — the three log names rest on it
    NFR-MNT-02  already requires 100% branch coverage of tenant-isolation code

Six clauses, nothing to add. Constitution principle VI is satisfied by citation.

**This list said four until analysis pass 12.** The last two arrived at pass 8 with FR-031, FR-032
and FR-027 and nothing came back to add them — the verdict *"no clause changes"* stayed true while
the enumeration behind it went stale, which is the same shape as every other list in this feature
that was written once.

**Appendix C is the part that is not automatic.** Chapter 3.19 closed open question 3 there
and recorded the diff; this chapter must state before implementing whether it touches
Appendix C at all. Read at `d38f415`: the six open questions are about sequence-number
scope, channel size, metering precision, dev-token limiting and emoji packs. **None is
about membership propagation**, so the expected answer is "no row changes" — and FR-002a
exists because "expected" is not "verified".
