# Implementation Plan — chapter 3.21, the typing indicator

**Spec**: [spec.md](./spec.md) · **Research**: [research.md](./research.md)
**Predecessor**: `part3-ch20` (fence predecessor is `git rev-parse part3-ch20^{commit}`)
**Created**: 2026-08-31

---

## Technical Context

| | |
|---|---|
| **Language** | TypeScript, Node.js (ADR-01, ADR-15) |
| **Services touched** | gateway (session, a new fabric module), protocol package |
| **Services NOT touched** | api, dispatcher, ClickHouse, NATS — this chapter writes nothing durable |
| **Fabric** | Redis pub/sub, a fourth subject grammar (R1) |
| **New state** | **none.** No table, no Redis key, no timer (R3) |
| **Frame changes** | one new INBOUND schema added to the union; `typingSchema` unchanged (R2, FR-008) |
| **Lane budget** | 240 s; the lane runs 228.8 s with 11.2 s of headroom (R9) |

**No NEEDS CLARIFICATION remain.** The spec left three open and research closed all three:
the grammar (R1), where the expiry lives (R3), and the renewal interval (R6).

---

## Constitution Check

**Four gates are genuinely engaged and one of them changes the design.**

### I. Tenant Isolation (NON-NEGOTIABLE) — **PASS, and it is the reason for FR-006**

A typing signal names a channel. If the gateway trusted a `user` from the payload, a client
could type as anybody — which is exactly what chapter 3.12's gauntlet row says about the
outbound frame. The identity comes from the connection, the way chapter 3.17 made the send
path resolve its sender, and the environment compared is the connection's own.

The new subject carries a channel id, which is a uuid and not an environment-scoped key, so
this is the fan-out's case rather than the limiter's for the `ioredis` exemption.

### II. No Acknowledged Message Is Ever Lost — **PASS, and it does not apply**

Every clause in II is about a *message*: acked after commit, ordered by server-assigned
sequence, idempotency keys at the storage layer, tombstones preserving sequence.

**A typing signal is none of those things.** It is not acknowledged, carries no sequence,
writes nothing, and has nothing to be idempotent about. Constitution II's obligations
attach to durability, and this chapter creates none.

**This is worth stating rather than skipping**, because chapter 3.20's phase order was
built entirely around II — publish-after-commit without an outbox row is the case II names
— and a reader coming from that chapter will expect the same shape. The reason it does not
recur is that 3.20 wrote a row and this chapter writes nothing.

### III. Two Data Paths, Never Crossed — **PASS, and R1 is this gate in disguise**

The operational path is the socket and Redis; the analytical path is NATS and ClickHouse. A
typing indicator touches neither the analytical path nor the database.

**The fourth subject grammar is the same principle one level down.** Carrying typing on
`chan:{channel_id}` would cross the message path with an ephemeral one, and ADR-19 already
refused that for presence with typed points as evidence — **seven of them, where that
record counts three**, and all seven still present.

### IV. Single Writer, Single Source of Truth — **PASS, vacuously, and that is the finding**

IV permits a lossy fabric because durability and resume live in PostgreSQL sequences and
cursors, and requires any new delivery mechanism to preserve that recovery property.
Chapter 3.20 met that with a backstop because a revocation has no cursor.

**A typing indicator needs no backstop, and the reason is not that it is unimportant.** A
dropped typing publish self-corrects in at most one renewal interval — 2 seconds — because
the client renews while the user keeps typing. And if the user has stopped, the correct
end state is *no indicator*, which is what a dropped publish produces.

**A lost typing frame converges on the truth. A lost revocation converges on a lie.** That
is the distinction IV is really about, and this chapter is the one that makes it visible by
being the opposite case.

### V. API-First, Developer-First — **PASS with an obligation**

A new inbound frame is public protocol surface. It must be in the union, in
`frames.test.ts`, and in the direction gauntlet with a stated direction and reason. It must
also be documented as the second thing a client may send, because twenty chapters of
documentation say there is one.

### FR-RTM-08 itself — **MET ON THE PLATFORM'S HALF, AND THE OTHER HALF IS THE CLIENT'S**

Not a constitution gate, and it belongs here anyway, because analysis pass 6 found five
passes had gone past it. The clause reads *"Typing indicators **shall** expire automatically
after 5 seconds without renewal and shall not be persisted."*

The second half is met absolutely: nothing is stored anywhere. **The first half the platform
cannot execute.** `typingSchema` carries no state field, so no frame exists with which a
server could end an indicator, and there is no SDK in this repository — the timer belongs to
the customer's own application.

So the verdict is *met, with the boundary named*, and it is recorded rather than asserted.
Chapter 3.20 did the same for FR-RTM-10: met on the happy path, bounded by an interval under
fabric loss, with the 55-second excess stated rather than hidden in a number nobody wrote
down. Chapter 3.18 refused to narrow a clause until the code passed.

**Why five passes missed it**: "the protocol has no stop frame, therefore the client holds
the timer" is a correct account of the mechanism and an elegant one, and it never asks whose
obligation the clause states. A derivation that satisfies the reader is not the same as a
requirement that is met.

### VI. Requirement-Driven, Test-Verified — **PASS with the coverage obligation**

The new fabric module is delivery-scope code and takes NFR-MNT-02's 100/100/100/100.
Chapter 3.20 reached it on three of four new files by listing the module's arms in the
phase that built them; this plan does the same in Phase 3.

### VII. Boring by Design — **PASS, and the fourth grammar is the thing to justify**

No new service, no new language, no new dependency. The grammar is the only addition, and
R1 states the rule it follows rather than arguing it afresh: a kind that cannot share a
payload type cannot share a subject.

**One gate moved after pass 1.** Principle VII — scope is a commitment — was passed on the
grounds that a third limiter operation was a small addition. It turned out to be an
addition that could not do the job, and removing it left the design smaller than planned:
no Redis key, no third operation, no edit to `limits.ts`. **The simplification came from
checking a premise, not from wanting a simpler design.**

**Nothing here is a conditional pass.** Chapter 3.20 had two, and both changed its phase
order; this chapter has none, which is itself worth recording — it is the first chapter in
four whose design the constitution did not move.

---

## Phases

**Eleven phases, and the ordering rule is the inbound seam.** Everything a client can
reach comes after the refusal that guards it is proven still to work.

### Phase 1 — Setup and the failing state observed
Pin the lane environment in `baseline.txt`. Verify the four premises R1–R4 by command
rather than by memory, and record the outputs. Write a test that a client uttering the
typing signal today is refused with `unknown_frame_type` and close 4002 — **red on purpose,
and the phase commit says so**, because that refusal is what this chapter narrows.

### Phase 2 — The protocol
The inbound frame's schema, added to the union. `typingSchema` untouched. Unit tests for
the new schema and for the union's membership. **The gauntlet's three tests go red here**
(`expect(members.length).toBe(10)`), which is the derived-list check firing on the build
that adds a frame — expected, and the phase records it.

### Phase 3 — The fabric
The fourth subject grammar in the protocol package, and the gateway module that publishes
and subscribes. **List the module's arms before writing them** — chapter 3.20 reached
100/100/100/100 on three of four files that way and 3.19 paid seven tests and a re-measured
battery for not doing it. **Two Redis clients, a publisher and a subscriber**, because
`fanout.ts:33` states the rule — a subscribed connection cannot issue ordinary commands and
`PUBLISH` is one. Chapter 3.20's module needed only a subscriber because its **api** did the
publishing; this module publishes from the gateway, so it needs both. Analysis pass 5 found
this plan and its task list both specifying one, which would not have run.

### Phase 4 — US1: Mai sees Tuan typing (P1) 🎯 MVP
The delivery path end to end, cross-instance. **The sharp test is the negative one that
shares a run with a positive**: a non-member receives nothing while a member receives, in
the same publish.

### Phase 5 — US2: the inbound seam (P1)
Widen `session.ts:948` from one type to a named set. Invert Phase 1's red test. Update the
gauntlet's DIRECTIONS table, its count, and its sample builder. **Assert the set's exact
membership and exact size**, which is what makes a third inbound frame a decision rather
than an accident.

### Phase 6 — US3: the renewal interval, in memory (P2)
A `Map` on the connection holding the last publish time per channel. **No Redis, no third
`operation`, and `limits.ts` is not edited** — analysis pass 1 found the existing bucket
cannot express a 2-second per-connection rule, and that a per-environment ceiling on top
would bound a rate the debounce already bounds. **The residual risk is the connection count,
and it is NOT FR-RTM-09's** — that clause caps connections per USER at five, so a tenant with
3,000 users holds 15,000 and complies. At 0.5 publishes per second per connection,
NFR-SCL-01's 10,000 per instance is 5,000 per second worst case, and the SAD calls that
clause *"a budget, not a measurement"* (R2). Analysis pass 7 read the clause this plan had
deferred to.

**FR-014 moved out of this phase.** A typing signal must not spend the message send quota,
and leaving that in a P2 story meant stopping after the MVP could ship a cosmetic feature
able to exhaust a customer's message budget. It is asserted in Phase 5.

### Phase 7 — The resume buffer, and what must not enter it
A typing frame arriving mid-resume is sent immediately and never buffered (FR-018). Chapter
3.20's FR-029 test passed twice with its subject deleted, for two unrelated reasons; this
phase reads that record before writing its own.

### Phase 8 — Failure, and the closed vocabulary
Fabric unreachable: socket stays open, nothing reaches the client, one logged event.
**Assert the SET of names an instance emitted**, not what a grep finds — chapter 3.20's
FR-032 said three names while the code emitted six, and the amendment is on record.

### Phase 9 — The documents
ADR-21 if the architecture record changes, and R1 says it does: a fourth grammar and the
rule that produced it. Amend the SAD's Redis table. Verify `git diff docs/04-srs.md` is
empty and record the Appendix C decision either way.

### Phase 10 — The chapter
Decide the fence set before writing a fence: run `check:fences` at HEAD and read what it
demands. Correct R8's three published claims — **two of them written by chapter 3.20 and
falsified by this one** — in both locales, with `check-prose.py` written and run red first.

### Phase 11 — Polish and close-out
Coverage pins, the battery, `gaps.md` with every carried status re-checked, traceability
re-derived from the shipped tree in both directions.

---

## Complexity Tracking

| Addition | Why it is not avoidable | What was rejected |
|---|---|---|
| A fourth subject grammar | ADR-19's typed points are intact and there are seven, not the three that record names; sharing `chan:` means editing the highest-volume path for the lowest-volume traffic | An enveloped payload on `chan:` — a union parse on every message on every instance, and `fanout.invalid_payload` per keystroke during a rolling deploy |
| A second inbound frame type | No frame lets a client say it is typing; the socket refuses everything but `message.send` | Making `typing` bidirectional — its payload names a user, so a client could type as anybody |
| A gateway-held debounce, per connection and channel | A publish per keystroke at 10,000 connections per instance | **A third limiter operation, which analysis pass 1 found cannot work** — that bucket is keyed per environment on a 60-second window, against a rule that is per connection, per channel and 2 seconds. And a per-environment ceiling on top, which would bound a rate the debounce already bounds |
| Nothing else | — | No Redis key, no server timer, no table, no outbox row, no backstop |

**The last row is the one to read.** Three chapters in a row added durable state or a
recovery mechanism. This one adds none, and the constitution check explains why that is
correct rather than lazy: a lost typing frame converges on the truth.

---

## The two counts, and the word estimate

**Kept apart from the start, and neither is allowed to do the other's job.** Chapter 3.17
established the practice with 16 taught / 27 fenced / 35 changed, and *"neither number was
ever asked to do the other's job"*.

    9    what the chapter TEACHES     -> drives the word estimate
         packages/protocol/src/frames.ts (the inbound schema)
         packages/protocol/src/typing.ts
         services/gateway/src/typing.ts
         services/gateway/src/session.ts (the seam, the debounce, delivery)
         services/gateway/src/isolation.itest.ts (the gauntlet's eleventh member)
         services/gateway/src/typing.itest.ts
         services/gateway/src/limits.ts — NOT edited, and the chapter says why
         docs/05-sad.md (ADR-21)
         docs/08-error-reference.md (the entry this chapter falsifies)

    ~20  what the chapter must FENCE  -> drives the chain, and the number is a
         PREDICTION. `check:fences` at HEAD in Phase 10 is what settles it, and
         chapter 3.20's prediction of that number was never made — it read the
         checker's 18 and used it.

    ?    files changed                -> re-derived from `git diff --name-only`
         against the predecessor at the very end. A first count is expected to be
         wrong.

**THE WORD ESTIMATE IS ~3,200, FROM ARGUMENTS RATHER THAN FILES.** Nine arguments:

    the fourth grammar, and the rule three chapters reached independently
    the second inbound frame in twenty chapters
    a published frame that cannot say "stopped"
    the expiry belongs to the client, and the clause says the system SHALL
    two Redis clients, because PUBLISH is an ordinary command
    the debounce, and the limiter that could not express it
    a customer-facing document this chapter falsifies
    what the previous chapter's two branches left incomplete
    5,000 publishes per second against a budget nobody enforces

Chapter 3.20 made seven and measured 2,999; 3.19 made five and measured 2,445. **The rate
per taught file is not an estimator** — 3.17 came in 45% below 3.15 and 3.16's agreement.

## Risks

- **The inbound seam is the highest-risk change here**, not the grammar. Twenty chapters
  of tests assert that exactly one frame type is accepted. Phase 5 widens that and every
  one of them has to keep meaning what it meant.
- **No tenth gateway integration file.** R9: seven of nine already spawn their own api and
  five of forty battery failures were a fixture failing to come up. This chapter's
  integration tests share an existing file or an existing api.
- **A forward reference this chapter falsifies was published yesterday.** R8's claims 2 and
  3 are chapter 3.20's, and correcting them is Phase 10's work rather than an embarrassment
  to be buried.
