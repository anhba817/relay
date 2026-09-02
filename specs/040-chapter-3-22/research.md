# Chapter 3.22 — research

Every finding below was produced by a command against the tree, and the command is
named. Three of the twelve contradict something published; one contradicts a
hypothesis a previous chapter recorded as eliminated.

---

## R1 — WHERE THE REFUSAL HAPPENS, AND THE FILE ALREADY CONTAINS THE RULE

**Decision: complete the handshake, then close with a new close code.** Not the
upgrade seam, and the reason is written into `session.ts` by chapter 3.8.

The spec named this as the chapter's real first decision. It turns out to be
governed by a rule already in the code, at `services/gateway/src/session.ts:641`:

> *"A refusal needs to say WHEN to come back. `Retry-After` is an HTTP header and a
> close frame has nowhere to put one... So an over-limit handshake is refused with
> an HTTP 429 on the upgrade request, which still has a response to write headers
> onto. That makes it deliberately unlike the 4001 path immediately below, which
> COMPLETES the handshake in order to close it — because EIR-WS-05 asks for a close
> code on a bad token, and a close code needs a socket to arrive on. **Two refusals,
> two shapes, each because of what it has to carry.**"*

So the test is not "which seam is nicer" but **what does this refusal have to
carry**. The rate limit went to HTTP for one reason only: `Retry-After`. And
**FR-004 forbids exactly that** — no interval makes a cap refusal succeed. Strip
`Retry-After` and HTTP's advantage is gone; what remains to carry is "you hold five
already", which a close code and a reason string carry perfectly.

The identity is available at either seam, checked rather than assumed:
`server.on("upgrade")` at `session.ts:630` already awaits `authenticate(api, token)`
and reads `result.identity.environmentId` before `wss.handleUpgrade`. So the upgrade
seam was a real option and is rejected on what it carries, not on what it knows.

**AND THE ARGUMENT HAS ALREADY BEEN MADE ONCE, FOR THE CLOSEST ANALOGUE.** This
item was drafted from the rule at `:641` and then `session.ts:715` was read, where
chapter 3.11 decided the same question for the quota refusal in almost these words:

> *"NOT `refuseUpgrade`. That writes chapter 3.8's raw 429 and its whole
> justification was `Retry-After` — a header a close frame has nowhere to put. A
> quota refusal declines that header on purpose, so **the argument for the HTTP
> shape evaporates with it**, and the shape that is left **reaches a browser where a
> failed upgrade's body does not**."*

That last clause is a fact this item did not have and it is stronger than the
reasoning it replaces: **a browser cannot read the body of a failed upgrade.** So
the HTTP shape is not merely unnecessary for a cap refusal — it is unreadable in the
primary client environment. Refusing at the upgrade seam would produce a refusal a
browser experiences as a bare connection failure with no code and no message.

The pattern to follow is therefore fixed, not invented — `session.ts:730`:

    sendError(ws, "<new error code>", message);
    ws.close(<new close code>, CLOSE_CODES[<new close code>]);
    logger.log("info", "connection.rejected", { reason: "<...>" });

An error frame first because a close reason is a short string, then the code. Three
refusals now share one shape and each declined `refuseUpgrade` for the same reason.

**Alternatives considered.** (a) HTTP 429 at the upgrade, reusing `refuseUpgrade` —
rejected twice over: it would send `Retry-After` on a refusal no interval fixes
(FR-004), and a browser could not read the body. (b) A 4xx status other than 429 at
the upgrade — rejected: same body problem, and it discards EIR-WS-05's precedent
that a connection-level refusal arrives as a close code, which `session.ts:626`
gives as the reason the `noServer` design exists at all.

---

## R2 — IT NEEDS A SIXTH CLOSE CODE, AND CHAPTER 3.15 ALREADY WROTE THE ARGUMENT

**Decision: a new close code. Not 4008, not 4001, not 4003.**

`packages/protocol/src/codes.test.ts:19` pins the exact set:

    expect(Object.keys(CLOSE_CODES).map(Number).sort()).toEqual([
      4001, 4002, 4003, 4008, 4009,
    ]);

Five codes, and the test makes a sixth a decision rather than an accident. The
argument for adding one is not new — chapter 3.15 made it to add `4003`, and
`codes.ts:10` records it:

> *"A banned user's token is perfectly valid... Closing 4001 tells a client to
> re-authenticate, which succeeds at minting a token and fails again at connect: an
> infinite loop against a wall. That is the same argument this file already makes
> for `wrong_credential_type` and `quota_exceeded` — 'a client that cannot tell them
> apart retries the wrong one for ever'. EIR-WS-06 names four classes to
> distinguish — authentication, quota, shutdown, protocol violation — and a ban is
> none of them."*

A cap refusal is none of the four either, and each reuse fails the same test:

| reuse | what the client would do | why it is wrong |
|---|---|---|
| `4008` quota exhausted | wait for the quota to reset | the remedy is closing a connection, available now; waiting never works |
| `4001` invalid token | re-authenticate | the token is valid; minting a new one and reconnecting loops for ever |
| `4003` banned | stop trying, tell the user they are barred | the user is not barred; four of their connections are working |
| `4002` protocol violation | fix the client | the client did nothing wrong |

**Alternatives considered.** An error frame with a new `ERROR_CODES` entry and an
existing close code — rejected because the close code is what a client branches on
when the socket closes, and an error frame arriving immediately before a
misleading close code is the case `codes.ts` calls out for `quota_exceeded`: the
frame carries the detail and the *code* still has to be right. This chapter ships
both, which is what chapter 3.11 did for 4008.

---

## R3 — THE STRUCTURE: THE SAD PRESCRIBES A ZSET, AND THE CONSTITUTION ARGUES AGAINST ITS ATOMICITY

This is the chapter's largest open question and the answer is not the published one.

**What is published.** `docs/05-sad.md:574`: *"A sorted set scored by heartbeat
time, pruned with `ZREMRANGEBYSCORE` on read, is the correct version."* Written by
chapter 3.20 in the same row that recorded the original defect. It is a table row,
not an ADR, which matters for how it gets amended.

**What the tree says about atomicity.** FR-013 requires that two attempts racing
for the last slot admit at most one. A ZSET cannot do check-and-insert in one
command: prune, count, add are three round trips. The options are a Lua script or an
optimistic add-then-verify, and both have a problem:

    Lua                     first script in the repository. `grep -rn "\.eval(|
                            defineCommand|\.multi("` over services and packages
                            returns ZERO hits — this platform has never issued a
                            multi-command Redis operation of any kind.
    add, count, un-add      4 held, two arrive: both ZADD (6), both count 6 > 5,
                            both ZREM, BOTH REFUSED. One should have been accepted.
                            Safe, and wrong.

**And Lua is a constitutional question, not a preference.** Constitution VII: *"One
language (TypeScript/Node.js) across services, SDK, and dashboard... **Introducing a
second language requires a superseding ADR with profiling evidence.**"* Whether an
embedded Redis script is "a language across services" is arguable — and the clause
says *"Disagreement attacks the driver, not the choice"*, so the argument is
available. But **this chapter cannot produce profiling evidence**: the lane's
largest membership set is five channels and NFR-SCL-01 asks about ten thousand
connections per instance. A chapter that cannot measure cannot discharge that
clause.

**Decision: five per-user slot keys, claimed with `SET NX PX` and renewed with
`SET IFEQ PX`.**

    conn:{env}:{user}:{slot}   slot in 0..4, value = the connection's id
    claim        SET key id NX PX <bound>        atomic, one command, no Lua
    heartbeat    SET key id IFEQ id PX <bound>   renews only if the value is
                                                 STILL THIS CONNECTION'S
    clean close  SET key - IFEQ id PX 1           frees immediately (FR-010), and
                                                 ONLY if the slot is still ours
    shutdown     the same, for every held slot    FR-011a, not the bound
    crash        the key's own TTL expires       per-member expiry BY CONSTRUCTION

Four things this gets that the ZSET does not:

1. **Atomicity from Redis rather than from application logic.** The claim is
   `SET … NX`, which `presence.ts:216` already uses: two racers cannot claim one
   slot, the loser walks to the next, and when all five are held both correctly
   refuse. FR-013 is satisfied by the command, not by a check-then-act.

   **The renewal is NOT a primitive this codebase already uses**, and the first
   draft of this point claimed it was — it cited `presence.ts:195`'s `XX` as though
   the design's renewal were the same call. It is not: the renewal is `IFEQ`, which
   appears nowhere else in this platform. That is a cost, recorded in `plan.md`'s
   complexity table: one unfamiliar flag against a compare-then-set that would be
   two commands and a race.
2. **The SAD's own complaint disappears rather than being worked around.** The
   defect recorded was *"a Redis TTL is per key, not per set member"*. Making each
   member a key means the TTL **is** per member. The ZSET works around the
   limitation with an application-level prune that must run on every connect; if it
   does not run, dead entries never leave.
3. **The renewal cannot take a slot it does not own** — `SET key id IFEQ id PX`
   refreshes only while the value is still this connection's id, and is refused both
   when the key holds somebody else's id and when the key is gone.

   **THIS POINT WAS WRONG IN THE FIRST DRAFT AND THE MEASUREMENT IS WHY.** It read
   *"`SET XX` cannot resurrect a released slot… `ZADD` has no such guard"*, citing
   `presence.ts:195`. `XX` tests **existence, not ownership**, which the lane's own
   Redis says plainly:

       SET k A EX 30      ->  OK        k = A
       SET k B XX PX 60000 ->  OK        k = B      it overwrote a value it did not own

   So the failure mode is worse than the resurrection it was chosen to prevent: a
   connection whose slot expired during a Redis outage longer than the bound comes
   back, finds the slot re-claimed by somebody else, and **its heartbeat silently
   takes it.** Both connections then refresh one key — six connections, five slots,
   FR-001 and FR-011 both violated.

   **And the analogy to presence did not transfer.** `presence.ts:195` refreshes a
   key whose value is the literal `"1"`: its value carries no identity, so ownership
   cannot be stolen. The slot key's value carries identity, and that difference is
   the whole question. A pattern was copied without checking whether the property
   that made it safe came with it — this project's own recorded failure mode, one
   level up from a regex matching the examples in front of it.

   **`IFEQ` is available and typed**, measured on the same server:

       redis_version                       8.10.0
       SET k C IFEQ B PX 60000     -> OK   k = C     right owner, renewed
       SET k D IFEQ WRONG PX 60000 -> nil  k = C     wrong owner, refused
       SET k A IFEQ A PX 60000     -> nil  absent    key gone, refused — which is
                                                     the signal FR-011 needs
       ioredis 6.0.0                       `IFEQ` present in RedisCommander.d.ts

   One command, no Lua, no cast. **The decision survives its own broken argument**,
   which is the outcome Constitution VII's "attack the driver, not the choice"
   describes — but an ADR resting on a false driver is not allowed to ship, so
   ADR-23 states this one.

   **AND THE RELEASE HAS THE SAME PROBLEM, WHICH THIS FIX INTRODUCED.** The first
   remedy changed the renewal to `IFEQ` and left the release as `DEL` — and `DEL`
   has no ownership check either. A connection whose slot expired during an outage,
   was re-claimed, and then closes cleanly would delete **the new owner's key**,
   freeing a slot that is in use. Found by asking what the fix made worse, which is
   the cheaper of the two habits chapter 3.21 recorded.

   There is a conditional release in one command, measured on the same server:

       SET k x IFEQ OWNER PX 1  -> OK   and EXISTS is 0 a moment later
       SET k x IFEQ WRONG PX 1  -> nil  value untouched
       GETDEL                    exists, and is unconditional — no use here

   So a release is `SET key - IFEQ id PX 1`: a one-millisecond tombstone written
   only if the slot is still this connection's. **The window has a consequence and
   it is the safe direction** — a claim landing inside that millisecond finds the key
   present and its `SET NX` fails, so it walks to the next slot. One slot briefly
   skipped, never an over-admit. A plain `DEL` has the opposite failure.
4. **No prune step means no prune bug.** There is no code path that can forget to
   prune, and nothing to test for it.

**The cost, stated rather than hidden.** Claiming a slot costs 1 to 5 round trips
instead of 3, and there is no cheap `ZCARD` — the count FR-015 wants to log is
"5 minus the free slots found during the walk", discovered rather than read.

**AND THE PERFORMANCE ARGUMENT I REACHED FOR FIRST DOES NOT HOLD.** The first
version of this item argued slots were *cheaper*: expected round trips ≈ 1.5 across
a realistic distribution of held connections, against the ZSET's flat 3. That is
arithmetic about a quantity nothing constrains. NFR-PRF-04 budgets **p95 < 1 s from
handshake to `connection.ack`**, and the whole difference is a few local
milliseconds. Round-trip count is not a reason to choose either design, and
presenting it as one would have been the same error as chapter 3.15's word-rate
estimator — a number that was easy to compute standing in for the number that
mattered.

**Alternatives considered.** (a) The SAD's ZSET with Lua — the correct shape,
blocked on Constitution VII without profiling evidence. (b) The SAD's ZSET with
add-then-verify — false refusals, shown above. (c) A single `INCR`/`DECR` counter —
rejected outright: a counter cannot expire per member, so one crashed instance
leaks a slot for ever, which is the original defect in a new shape.

**AND THE PERIODIC COST DOES NOT REOPEN IT.** Analysis pass 12 measured the renewal's
steady-state load — 500 `SET`/s per instance at NFR-SCL-01's ten thousand connections,
against presence's 200/s — and that figure bears on the rejected alternative, so it is
answered here rather than left hanging in `plan.md`:

    rate         a ZSET renews with one ZADD per connection per interval.
                 IDENTICAL: 500/s either way
    key count    2,000 sorted sets against 10,000 slot keys. The ZSET wins 5:1
    on connect   prune + count + add = 3 commands, against a walk of 1 to 5
    expiry       one TTL for five members — the original defect, unchanged

**The ZSET is cheaper on exactly one axis and it is the one nothing constrains.**
Neither figure moves the decision: Constitution VII's bar on a second language is
untouched, and per-member expiry is the property the chapter needs. Recorded because
an ADR whose rejected alternative turns out cheaper on an axis nobody checked is how a
driver gets attacked later.

**What this obliges the chapter to do.** Contradicting a published SAD row is not
free. The chapter owes an ADR stating drivers, rejected alternatives and a reversal
condition (Constitution VII), and it owes the SAD amendment FR-017 already requires
for a different reason. **Reversal condition to state in the ADR:** if a future
chapter needs the count of a user's connections without knowing the slots — a
dashboard, an admin API — five reads to answer "how many" becomes the wrong shape
and the ZSET returns with Lua and the profiling evidence that would then exist.

---

## R4 — THE TWO INTERVALS, AND WHY NEITHER IS 30,000

**Decision: bound 60,000 ms, heartbeat 20,000 ms. Three heartbeats per bound.**

The SAD's row already says *"60 s, heartbeat-refreshed"* for `conn:`, and that
number is kept. The heartbeat is derived, not chosen:

    bound      60_000   the SAD's stated TTL for this key
    heartbeat  20_000   three per bound, so TWO consecutive misses do not free a slot
    margin              40_000 ms between the last successful heartbeat and expiry

Chapter 3.19 established the rule and paid for both halves of it, and both lessons
are shipped code: *"a TTL equal to its refresh interval expires a connected user"*
(`presence.ts:41`), and *"arming a grace check at exactly `graceMs` puts two
deadlines on one instant reached by two clocks"*. Presence uses TTL 30,000 with
refresh 10,000 — three per window — and this is the same ratio at twice the scale.

**`PING_INTERVAL_MS` is 30,000 and is deliberately NOT reused.** It is at
`session.ts:48` and it is the third quantity in the family chapter 3.19 warned
about. A slot heartbeat riding the protocol ping would tie a Redis TTL to a
client-visible keepalive: change the ping and slots start expiring. Separate timer,
separate number, and the tests assert the ratio rather than the values.

**Why the bound cannot be much shorter.** It is how long a crashed tab holds a
slot, which the spec's Q1 clarification names as the accepted cost of refusing the
newest. Sixty seconds is the published figure and the chapter does not relitigate
it; **what the chapter owes is a test that the slot is still held at 59 s and free
after the bound**, because that is the only externally visible consequence.

---

## R5 — FR-RTM-09's SECOND CLAUSE IS ALREADY TRUE, AND THE CODE SAYS SO IN WORDS

**Finding: delivery walks connections, not users. Story 3 adds tests, not
behaviour** — which is what the spec predicted, now confirmed.

`session.ts:283`, `:335`, `:365` and `:406` all iterate
`registry.subscribersOf(channelId)` or `registry.connectionsFor(user)`, and
`registry.ts:101` returns every connection whose identity matches. The intent is
stated at `session.ts:310`: *"That function walks `subscribersOf` and sends to
everyone, so a user sees their own presence transition"*, and at `:321`: *"a user
may hold several connections. A socket comparison would show a user their own
indicator on their own second device."*

So FR-014 is a property of shipped code. The chapter's obligation is a test that
would fail if it stopped being true — which is not the same as a test that passes
today. **The falsification to run before writing it:** change one delivery site
from `subscribersOf` to a de-duplicated-by-user list and confirm the new test goes
red. A test that cannot be made to fail by breaking its subject proves nothing, and
this chapter has three of them to write.

---

## R6 — `policy.ts` DIVIDES BY FIVE AND THE ANSWER IS NOT THE NUMBER IT SHIPPED

**Finding, and it is not this chapter's to fix.** `services/api/src/limits/policy.ts:36`:

> *"NFR-SCL-01's ten thousand connections per gateway instance, divided by
> FR-RTM-09's five per user, re-established inside one window so a deploy stays one
> reconnection cycle (NFR-REL-03)."*

    10_000 / 5              = 2_000
    the shipped constant    = 3_000        policy.ts:43
    pinned by a test        policy.test.ts:54

And the test that pins it says, in its own comment, *"the chapter states the
derivation and this asserts the result"* — so the assertion delegates the arithmetic
to prose, and the prose yields a different number.

There is a further unit problem underneath the discrepancy. The limiter counts
**establishments** (`operation: "connect"`, one `spend` per upgrade at
`session.ts:665`). Ten thousand connections re-established in one window is
**10,000 establishments**, not 2,000; dividing by five converts connections to
*users*, which is not the unit being limited. So the stated derivation produces
2,000, the correct figure for its stated goal is 10,000, and the shipped value is
3,000 — three numbers, and the comment claims *"each number below names what it
rests on"*.

**Why it matters now.** Until this chapter, five was enforced nowhere, so the
division was a sizing estimate against a hypothetical. When the cap becomes real, a
deploy makes every user reconnect five connections and this limit is what throttles
the recovery — the exact thing NFR-REL-03 bounds and the exact failure the comment
says it fixed when it replaced 60/min.

**Owner: whoever revisits FR-RTL-01.** This chapter states the arithmetic, does not
change `connect: 3_000`, and does not touch `policy.test.ts` — the spec puts the
connection-rate limit out of scope, and a chapter that quietly re-tunes another
chapter's shipped limit while shipping a cap would make two changes impossible to
tell apart in a battery. It goes to `gaps.md` with this item's numbers.

---

## R7 — THE LANE'S PORT MAP IS NOT MERELY INCOMPLETE. ONE UNREGISTERED RANGE CONTAINS A REGISTERED ONE

Chapter 3.21's `gaps.md` item 4 says the authoritative map in `limits.itest.ts:16`
lists seven ranges for nine files and names the two missing. **It undercounts.**
Read from the allocation lines rather than the map:

    limits.itest.ts          4100 + %200   = 4100-4299   registered as 4100-4300
    dispatcher.itest.ts      —             = 4310-4370   registered
    session.itest.ts         4400 + %200   = 4400-4599   registered as 4400-4600
    meter.itest.ts gateway   4610 + %60    = 4610-4669   registered as 4610-4670
    presence.itest.ts  api   4700 + %200   = 4700-4899   NOT REGISTERED
    meter.itest.ts     api   4710 + %60    = 4710-4769   registered as 4710-4770
    isolation.itest.ts       4900 + %200   = 4900-5099   registered as 4900-5100
    public-surface.itest.ts  5200 + %200   = 5200-5399   registered as 5200-5400
    membership.itest.ts      5400 + %200   = 5400-5599   NOT REGISTERED

**`presence.itest.ts`'s range strictly contains `meter.itest.ts`'s api range.**
Both spawn an api. `services/gateway/vitest.integration.config.mts` sets no
`fileParallelism`, so vitest's default applies and those two files run
concurrently. P(same port) = 60 × (1/200)(1/60) = **1/200, 0.5% per run.**

**AND THIS INVALIDATES AN ELIMINATION A PREVIOUS CHAPTER RECORDED.** Chapter 3.20's
chapter 3.20's `gaps.md` item 19a lists three hypotheses "measured and eliminated", one of them *"a
port collision (the failing ports are in each file's own range)"*. That test cannot
detect this collision, **because the colliding port is in each file's own range** —
the ranges overlap. The property checked was not the property at issue.

The two files with open, unexplained battery failures are these two:
`presence.itest.ts` (one of 3.20's four, `fetch failed`) and `meter.itest.ts`
(chapter 3.21's run 8, `no ack within 5s`). **0.5% per run does not account for an
observed 2.5–5% for those files**, so this is a contributing mechanism at most and
is recorded as arithmetic, not as the cause. It is also the first hypothesis in that
item with a number attached.

There is also a second, more accurate map already in the tree.
`membership.itest.ts:217-233` records its own two failed attempts — *"the first
picked 4900–5099, which is `isolation.itest.ts`'s range exactly; the second picked
5000–5199, which still overlaps it by a hundred ports, because that file's `4900 +
(… % 200)` reaches 5099 and reading only its first number misses it"* — and carries
a local map listing `4700–4899 presence`. **Two maps in one package, and the
unauthoritative one is right.**

**Decision for this chapter: take no range, and fix the map anyway.** Story 2 needs
two gateway instances, and chapter 3.21 showed gateways boot in process on
`server.listen(0)` with a stubbed api client, so no port is claimed and no api is
spawned. The map fix is therefore not owed by the rule in item 4 ("the next chapter
that takes a range owns it") — and is done regardless, because this chapter is the
one holding the measurement. Two chapters fence `limits.itest.ts`, so the edit costs
two regenerated diffs and that cost is stated in the task.

---

## R8 — WHAT THE GATEWAY MAY CALL, AND WHY THE API IS NOT ASKED

**Decision: the gateway enforces the cap directly against Redis. The api is not
involved.**

The cap's state is connection state, and Constitution IV puts the api in charge of
**persisted** state, not ephemeral state — presence (chapter 3.19) and typing
(chapter 3.21) both keep their state in Redis from the gateway for the same reason,
and `presence.ts` owns its own client. FR-RTM-08's *"shall not be persisted"* set
the precedent one chapter ago; a connection registry is the same class.

Asking the api would also put a database round trip on the handshake path and give
the api a table describing sockets it cannot see, which is the shape ADR-05 exists
to prevent (*"the gateway never writes to the database"* — `session.ts` cites it at
the upgrade handler).

**Module shape follows the two files that did this before.** A new
`services/gateway/src/connections.ts` owning its own `ioredis` client and declaring
the narrow command interface it needs, the way `presence.ts` declares `set`/`del`
and `typing.ts` creates its own publisher and subscriber. One `error` listener per
client — chapter 3.18's R10 found `createFanout` without one while both rate
limiters had one and explained why.

---

## R9 — FAILING OPEN IS NOT FREE, AND THE LOG LINE CARRIES THE REQUIREMENT

The spec's Q2 decided fail-open. What research adds is **where the evidence lives**,
because chapter 3.18 found the general case: *the fan-out's `publish` swallows its
own errors and resolves, so "the send returned 201 while Redis was down" is true of
a publisher that does nothing at all — the assertion that carries the requirement is
the log line.*

A cap that fails open is exactly that shape: from outside, "the connection was
accepted" is identical whether the cap was checked and satisfied or not checked at
all. So FR-016a's log line is the only observable difference, and the test for
FR-016 asserts **the log line**, not the acceptance.

`presence.ts:232` already has the pattern — a `failable(op, work)` wrapper that
catches, logs with an operation name, and returns `null` so the caller can
distinguish "no" from "could not ask". The cap reuses that distinction: `null` means
unenforced and is logged; `0` means no slots held.

---

## R10 — COVERAGE IS MEASURED IN THE PACKAGE THAT OWNS THE FILE

`services/gateway/src/connections.ts` is a gateway file, so its coverage is measured
by the root coverage lane, which includes `services/*/src/**/*.ts` and both
`*.test.ts` and `*.itest.ts` (`vitest.coverage.config.mts:88`). No repeat of the
recorded trap where `GET /internal/memberships` had five integration tests in the
gateway package and read 28.57% statements, 0% branches because the api's coverage
is measured in the api package.

**Pin it at 100/100/100/100 and list the arms before writing them.** Chapter 3.21
did that and three of four new files hit 100 on the first run; chapter 3.19 met the
same requirement at close-out and paid seven tests, a deleted branch and a
re-measured battery. The arms visible from the design already: the `SET NX` miss on
each of five slots, the walk finding no free slot, **`SET IFEQ` refused because the
key is gone**, **`SET IFEQ` refused because the key holds another connection's id**,
the `failable` catch, a conditional release refused because the slot is no longer
ours, a conditional release for a slot the connection never held, and the shutdown
release with nothing held.

**And `**/main.ts` is excluded from coverage** (`vitest.coverage.config.mts:97`),
which is chapter 3.21's `gaps.md` item 8: the feature was inert in the product
because `main.ts` never passed the module to `attachSessions`, and no coverage
number could have shown it. This chapter adds a constructor argument to
`attachSessions`, the same seam. **The outsider test is not optional here** —
`packages/outsider/src/integrate.itest.ts` is the only instrument that boots the
shipped binary, and it is what found the inert feature.

---

## R11 — THE RACE TEST HAS TO FORCE THE RACE, NOT HOPE FOR IT

FR-013's scenario — two attempts for the last slot — is the kind of test chapter
3.21 wrote twice and got wrong once. Two recorded lessons apply directly.

**A task claiming "the ordering is the requirement" is claiming an observable
difference, and that claim needs falsifying before the test is written.** Chapter
3.20 specified two orderings as requirements and neither was observable. So before
writing the race test: remove the atomicity (use `SET` without `NX`) and confirm the
test goes red. If it stays green with a non-atomic claim, the test is not testing
the race.

**And `Promise.all` of two connects does not force a race.** Both calls reach Redis
through one client with one socket; the commands serialise. Forcing it needs two
clients, or two in-process gateway instances, which Story 2 already builds. The
honest version of this test may be that **`SET NX` makes the race unobservable from
the application**, in which case the test that carries FR-013 asserts the invariant
(never six held) across many concurrent attempts, and the record says the ordering
itself could not be observed. Chapter 3.21 has that sentence twice.

---

## R11a — NOTHING RELEASES A SLOT ON A DEPLOY, AND THE MECHANISM THE SPEC NAMED DOES NOT EXIST

Two facts, both read from the tree after the plan was written.

**There is no 4009 drain path in the gateway, and a test forbids one.**
`services/gateway/src/session.test.ts:965` says it outright — *"4009 IS STILL
EMITTED BY NOTHING. Chapter 3.11 gave the gateway its first…"* — and `:982` asserts
it:

    expect(text).not.toMatch(/close\(\s*4009/)

The spec's edge case named that code as the mechanism by which a drained instance
frees its slots. **It named a path that does not exist**, which is the same class as
`docs/05-sad.md:167` describing a registry nobody built — and it was written in the
same document that found the SAD's version.

**And the ordinary shutdown does not close sockets either.** `main.ts:124`'s
`shutdown()` awaits each module's `close()`; the session module's is:

    close: async () => {
      clearInterval(heartbeat);
      meter.stop();
      await meter.reportOnce(new Date());
      wss.close();
    }

`wss.close()` stops the server accepting connections and closes the HTTP server. It
does **not** close established client sockets. So on a deploy the process exits, the
OS tears down the TCP connections, and whether each connection's `close` handler
ever runs is a race with process exit.

**Which puts a 60,000 ms bound against NFR-REL-03.** That clause allows a deployment
*"no more than a single client reconnection cycle"*. A user whose five connections
were on the replaced instance is refused for up to a full bound — five slots held by
a process that no longer exists. **That is not one cycle, and no clock skew or bad
luck is required: it is the ordinary path.**

**Decision: the module exposes `releaseAll()` and `shutdown()` calls it**, before the
process leaves. Deleting five keys per held connection is cheap, it needs no new
close code, and it does not touch the test at `session.test.ts:982`. FR-011a states
the obligation; SC-013 states the observable.

**Alternatives considered.** (a) Emit 4009 on drain and release as each socket
closes — rejected: it turns a passing test red for a reason unrelated to this
chapter, and chapter 3.11 already decided 4009 stays unemitted. (b) Shorten the bound
so a deploy costs less — rejected: the bound is `docs/05-sad.md:574`'s published
figure and shortening it to paper over a missing release would make crash detection
worse to fix a case that is not a crash. (c) Accept it and document — rejected: it
fails a P2 clause on the ordinary deploy path.

---

## R11b — THE CAP IS OPT-IN PER FIXTURE, BECAUSE EVERY GATEWAY MODULE IS OPTIONAL

`session.ts` declares its modules as optional named parameters:

    fanout?: Fanout          session.ts:192
    limits?: GatewayLimits              :206
    presence?: Presence                 :217
    membership?: Membership             :222
    typing?: Typing                     :231

and all three in-process integration files call `attachSessions` directly with their
own module list rather than going through `createServer`. **So a fixture that does
not pass `connections` enforces no cap** — and none of the existing ones will.

**THIS ITEM SAID THE OPPOSITE FOR A WHOLE ANALYSIS PASS.** Its first version measured
that `typing.itest.ts:94` defaults to a constant `"env-1"`, that `resume.itest.ts`
hardcodes the same in seven places, that both lean on `user: "tuan"`, and that the
files run in parallel — all true — and concluded that their connections would compete
with the new file for `conn:env-1:tuan:*`. **They will not compete, because they will
claim no slots at all.** The premise was never checked: nobody asked how a fixture
receives a module.

What survives, and what does not:

    the per-run environment for the new fixture   KEPT — its own tests must not leak
                                                 into each other. **But it is not the
                                                 ONLY enforcing fixture**: Phase 1
                                                 found that T011's red test needs the
                                                 module passed into
                                                 `session.itest.ts`'s "cap at the
                                                 door" block or it can never go
                                                 green, so that block enforces it too
                                                 (T042d). Two fixtures, deliberately,
                                                 and the second is where the other
                                                 two door refusals already live.
    the teardown DEL of its own keys              KEPT — this file deliberately fills
                                                 all five and a 60 s TTL outlives the
                                                 package's ~45 s run
    the 4-of-5 headroom measurement               DROPPED — it measured demand that
                                                 will not exist
    "editing two fenced files to buy headroom
     nobody is using"                             MOOT

**And it makes one shipped comment unwriteable as planned.**
`presence.itest.ts:728` says *"FR-RTM-09's five is enforced NOWHERE"* and opens five
connections because nothing stops it. That sentence stays **true in that file** after
this chapter, because that fixture passes no `connections` module. A task that
annotated it with "this test now sits exactly at the cap" would be writing a false
claim into a test file — which is the failure chapter 3.21 recorded four times over in
its own test titles.

**THE DECISION THIS FORCES: optional, like every other module.** Required would make
the inert-feature failure impossible to repeat — the compiler would catch a fixture
that forgot it — but it breaks three fixtures, two of them fenced by earlier chapters,
for a cap those fixtures do not test. Optional keeps the cost down and puts the whole
weight on two tasks: the `attachSessions` argument in `main.ts` and the sealed
outsider test that boots the shipped binary.

**That is the same bet chapter 3.21 lost.** Its `typing?` was optional, `main.ts` never
passed it, and the feature was inert while 1,174 coverage tests were green. The
difference this chapter is relying on is that the bet is now named: the outsider test
is a plan requirement rather than a polish item, and `main.ts` has two separate tasks
that each say the other does not substitute for it. **If that is not enough, the next
chapter to add a module should make them all required and pay the fixture edits once.**

---

## R11c — WHAT THE LOSING CONNECTION DOES, WHICH NOTHING SAID FOR FIVE PASSES

`IFEQ` made the renewal safe and left a question nobody asked: **the renewal can be
refused, and the connection is still open.** `data-model.md` named the state and
deferred — *"what it does next is the plan's call"* — and the plan never made the
call. Analysis pass 5 found it by grepping the artifacts for the state rather than
for a symbol.

**The consequence is that the cap is exceeded by the mechanism built to enforce it.**
A connection whose slot expired during an outage and was re-claimed keeps serving
with no slot: six open connections against a count of five, FR-001 broken, and no
test in the chapter looks from the connection's side — T056 covers the expired slot
and T056a the hijack, both from the registry's.

**Decision: re-claim once, then branch on why that failed.** Every branch reuses a
decision this chapter has already taken.

    renewal refused, a slot is free      claim it, update the slot held in memory,
                                         carry on. THE COMMON CASE after any brief
                                         outage, and the user is under the limit
    renewal refused, all five held by
    other connections                    the cap is genuinely exceeded; close with
                                         the same code and message a refused sixth
                                         connection gets, because that is what it
                                         means
    the registry cannot be reached       FR-016: keep the connection, log that the
                                         cap is unenforced. Refusing here would
                                         punish a user who is under the limit for
                                         Redis being down

**The middle branch is the only one that closes an established connection**, and it
is worth naming against FR-005 — *refusing a connection must not close one the user
already holds*. FR-005 governs a **refusal**: opening a sixth must not cost the five.
This is not that. Here the connection has already lost its place to a competitor and
the choice is between closing it and running over the cap. **The two rules do not
conflict; they are about different events**, and a reader who finds them adjacent
needs that sentence.

**Alternatives considered.** (a) Close on any refused renewal — rejected: after a
brief outage nothing else took the slot, so it closes a connection that is entitled
to one, and a client that reconnects on close gets it straight back, which makes the
close pure cost. (b) Keep serving and log — rejected: it is FR-001 violated with a
log line as consolation, and chapter 3.18's lesson is that a log line is the
assertion that carries a requirement, not a substitute for the behaviour. (c) Close
and let the client reconnect for the re-claim — rejected: the re-claim is one Redis
command and a reconnect is a full handshake plus a backfill.

---

## R12 — WHAT COULD NOT BE ESTABLISHED

- **Whether five is still the right number.** Nothing in the SRS derives it, and
  `policy.ts` divided by it in a comment. This chapter enforces the published
  figure; it does not defend it. Recorded so the question exists in writing.
- **Whether the slot design holds at NFR-SCL-01's scale.** 10,000 connections per
  instance at five per user is 2,000 users and up to 10,000 slot keys per
  environment. Trivial for Redis by inspection; unmeasurable on this lane, whose
  largest fixture is five channels. NFR-SCL-01 is verified by analysis (`A`) and
  remains undischarged per the SRS's Appendix C — this chapter does not change that.
- **Whether the presence/meter port overlap is the mechanism behind either open
  battery failure.** 0.5% per run is a real number against an observed 2.5–5%, so
  it is a contributor at most. The way to settle it is not more runs: it is the
  evidence capture from chapter 3.21's `gaps.md` item 9, which five files still
  discard.
