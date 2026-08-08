# Phase 0 — Research: Chapter 3.3, The Outbox

Checked against the repository at the `part3-ch2` state, not assumed. Sources:
`docs/04-srs.md` (FR-WHK-02, FR-ANL-04/06, NFR-REL-02), `docs/05-sad.md`
(§4.1 service responsibilities, §5.1, §6.1's `outbox` definition, §7),
`docs/06-adr-deep-dives.md` (ADR-02, ADR-06, ADR-07), the constitution
(Principles II, III, IV, VI, VII), and the current code.

---

## R1 — Where the event row is written

**Decision**: inside `Repository.sendMessage`'s existing transaction, as one more
`INSERT` before it returns.

**Verified**: `sendMessage` already opens `db.transaction(async (tx) => …)` — it
has since 2.2, because the sequence assignment needs a row lock. There is no new
transaction to introduce and no call site to change: both doors (the public REST
route and the socket's internal route) reach this one method, so both produce
exactly one event by construction (ADR-04's single write path, paying off again).

**The case that must not produce an event**: a recognised idempotent retry.
2.3's conflict path returns the ORIGINAL message and writes nothing — "a
recognised duplicate wrote nothing, so it consumes nothing". It must consume no
event either, or a client retrying on a flaky link would fire a second webhook
for one message. The outbox insert therefore belongs on the *inserted* branch
only, and that is a test, not a comment.

**Alternatives considered**: a database trigger on `messages` (rejected: it moves
business logic into the schema where ADR-04 says one codebase owns invariants,
and it would fire for backfills and repairs too); an application-level "after
commit" hook (rejected: that is precisely the bug this chapter is about).

---

## R2 — The relay loop

**Decision**: `SELECT … FOR UPDATE SKIP LOCKED` over unpublished rows, oldest
first, in batches; publish each; mark published; commit. Poll on an interval when
idle.

**Rationale**: ADR-06 specifies this shape and gives the reason `SKIP LOCKED`
matters — competing relays skip each other's batches, so horizontal scaling is a
property of the query rather than of a coordination mechanism. Two relays running
against one table is the *normal* deployment, not an edge case, because the api
service is stateless and runs more than once.

**Batch and interval**: to be fixed in Phase 1 and stated in the chapter as
numbers with reasons, not defaults nobody chose. FR-ANL-04's 60-second bound is
the only external constraint and it has two orders of magnitude of headroom, so
the interval is chosen for tidiness (a small number of wakeups per second) rather
than for latency.

**Alternatives considered**: `LISTEN`/`NOTIFY` to wake the relay immediately
(rejected for this chapter: it is an optimisation on a latency budget with 100×
headroom, and it adds a second delivery mechanism that can itself be missed —
the poll would still have to exist as the correctness path); a queue table with
advisory locks (rejected: `SKIP LOCKED` is the same thing with less machinery).

---

## R3 — What "published" means, and the at-least-once cost

**Decision**: publish, wait for the broker's acknowledgement, then mark the row
published in Postgres. A crash between those two steps republishes on restart.

**Rationale**: the alternative ordering — mark then publish — turns the
at-least-once guarantee into an at-most-once one and reintroduces exactly the
loss this chapter exists to remove. ADR-06 states the consequence plainly:
"at-least-once forever (embraced, not mitigated)".

**Where the duplicate is absorbed**: at the consumer, on the event's identity
(R7). Consumers do not exist yet — 3.4 builds the first — so this chapter's job
is to make the identity *available* and to say clearly that a consumer which
ignores it is broken.

---

## R4 — Proving the crash-in-the-gap property

**Decision**: a child process, killed by the parent with `SIGKILL` at a marker it
prints between commit and publish. Two modes — naive publish-after-commit, and
outbox — run against the same kill.

**Rationale**: the property under test is "what survives when the process stops
existing". A test that simulates the crash by throwing an exception proves
something weaker: it proves the code's own error path, which a real `SIGKILL`
never reaches. Chapter 2.8 established the child-process harness and 2.7 used a
deliberately hostile interleaving; this is the same discipline applied to
durability.

`SIGKILL` from the parent, not `process.exit()` from the child, because a child
that exits cooperatively can flush, and flushing is the thing being disproved.

**What each mode must show**:

| Mode | After the kill | The point |
|---|---|---|
| naive | message committed, no event anywhere | the failure is silent — nothing errored |
| outbox | message committed, event row present and unpublished | the event survived the process |
| outbox, after restart | relay publishes it | recovery needs no operator |

**Alternatives considered**: a fault-injection flag inside the service (rejected:
it would ship a code path whose only purpose is to break, and Principle VII);
`kill -STOP` and inspect (rejected: a paused process still holds its
transaction — it proves nothing about durability).

---

## R5 — Where the naive implementation lives

**Decision**: in the chapter's demonstration script under `scripts/`, never in
`services/`.

**Rationale**: the spec's checklist raised this, and 2.7 answered the same
question the same way: the broken version is a teaching artifact, so it lives
where teaching artifacts live (`scripts/split-brain.mjs` is the precedent). Two
consequences follow. It is fenced and therefore maintained — a broken example
that stopped compiling would be worse than none. And no service ever contains a
publish-after-commit path, so a reader copying the repository cannot
accidentally ship the bug.

---

## R6 — The subject, and how little of it this chapter owns

**Decision**: publish on `events.msg.created.{environment_id}`, the shape SAD
§6.1's own comment gives (`-- e.g. events.msg.created.{env}`). One stream,
`events.>`, file storage, created by the relay if absent.

**Bounded deliberately**: subject *taxonomy* — the full event-type list of
FR-WHK-02, per-environment sharding, stream retention and replication — is
chapter 3.4's, along with every consumer. This chapter creates the minimum a
publisher needs in order to be provable, and says so. A relay that publishes
into a broker with no stream is not a durable event spine; it is a fire-and-forget
send, which ADR-07 already rejected for a different path.

**Alternatives considered**: publishing with core NATS and leaving JetStream
entirely to 3.4 (rejected: the chapter's claim is that events cannot be lost, and
core NATS drops what nobody is listening for — the claim would be false at the
last hop); deferring the broker entirely and proving the relay against a stub
(rejected: then "the broker was down" and "the backlog drained" are untested
assertions, and they are two of this chapter's six success criteria).

---

## R7 — Event identity

**Decision**: an application-generated UUID carried in the payload as `id`, and
sent to the broker as the message's deduplication id.

**Rationale**: consumers deduplicate on event identity, and that identity has to
survive a republish — so it must be written once, inside the transaction, and
re-read on retry rather than regenerated. The outbox's `BIGSERIAL` is the relay's
cursor and is not a good event id: it is meaningless outside this database, and
it would leak the platform's event volume to every customer who receives one.

**Consequence**: `outbox.payload` is written complete inside the transaction.
Nothing is added at publish time, which keeps the relay a mover of bytes rather
than an author of them.

---

## R8 — Ordering, stated rather than promised

**Verified**: nothing in `docs/04-srs.md` requires event ordering. FR-MSG-03
orders *messages within a channel*, which the sequence number already delivers on
the read and delivery paths.

**Decision**: the relay does not guarantee cross-event ordering at the broker,
and the chapter says so in those words. Two relays with `SKIP LOCKED` may publish
concurrently; a batch that fails midway republishes from an earlier point. What
consumers get is every event at least once, each carrying the channel sequence
that *does* order it.

**Rationale**: this is the single most likely thing for a reader to assume and
then be hurt by later. Saying "we do not promise ordering, and here is the field
that does order what matters" is cheaper now than a webhook consumer built on a
wrong assumption in Part 3.5.

---

## R9 — The broker is not on the write path

**Decision**: the relay connects lazily and independently of request handling.
The api starts, accepts writes, and commits events with the broker unreachable;
rows accumulate; the relay drains when it returns.

**Verified against §7's own claim**: the failure matrix says "broker down, events
accumulate in Postgres, relay drains on recovery". That is a property this
chapter can actually test — stop the container, write, start it, assert the
backlog drains — and it is SC-007.

**The inversion to avoid**: a service that will not start without the broker has
made the event spine a dependency of the write path, which is the opposite of
what an outbox is for.

---

## R10 — Where the relay runs

**Decision**: inside the api service, started with the application and stopped
with it — ADR-06's own decision ("a small loop inside the API service initially,
promotable to its own deployment if outbox depth alarms fire").

**Consequence for tests**: the relay must be startable and stoppable in isolation,
because most integration tests want a quiet database. It is therefore a module
with an explicit start/stop rather than a timer that begins at import time, and
the suites that do not want it simply do not start it.

**Consequence for the chapter**: "promotable" is a claim, so the chapter should
show why it is true — the relay reads a table and writes to a broker, and it
shares nothing else with the api process.

---

## R11 — The dependency, and the fence budget

**Verified**: no NATS client exists in the workspace. `nats@2.29.3` is the
current release of the monolithic client; `@nats-io/jetstream@3.4.0` is the
modular successor. One of them joins `services/api/package.json` — the decision
belongs in Phase 1, on the basis of which one imports cleanly into a CommonJS
NestJS service, tested rather than assumed.

**MEASURED (T004, 2026-08-08).** Both candidates were installed in a scratch
CommonJS package, `require()`d the way the compiled api will load them, and used
to create a stream and publish one message to the compose broker.

| Candidate | `require()` from CJS | Stream + publish | Packages needed |
|---|---|---|---|
| `nats@2.29.3` | works | `seq=1`, ack carries `stream` and `duplicate` | **1** |
| `@nats-io/jetstream@3.x` | works | `seq=1` | **2** — it also needs `@nats-io/transport-node@3.4.0` |

The interop worry that motivated running this first — 2.6's `ioredis` TS2351 —
**did not materialise for either**. Both are usable, so the decision falls to
Principle VII instead: `nats@2.29.3` does the same job with one dependency where
the modular split needs two, and the api's manifest is fenced by three published
chapters, so every entry added there is an amendment somebody has to read.

**Decision: `nats@2.29.3`.** The modular v3 line is the successor and this will
want revisiting when v2 stops being maintained; that is a version-bump pass
(docs/07 stage G), not a chapter.

A note for the chapter: the first attempt at the modular candidate failed with
`Cannot find module '@nats-io/transport-node'`, because `@nats-io/jetstream`
carries no transport of its own. That is not a defect — it is the modular
design working as intended — but it *is* the second package, and finding it by
running the code rather than by reading the README is exactly why T004 runs
before anything is built.

**Fence budget, costed at planning time this time.** Chapter 3.2's notes record
that the fence bill was measured only after the fact and came to 41 fences. The
files this chapter is expected to touch that earlier chapters have already
fenced:

| File | Why it changes |
|---|---|
| `services/api/src/db/schema.ts` | the `outbox` table |
| `services/api/src/db/repository.ts` | the event insert inside the transaction |
| `services/api/src/app.module.ts` | the relay module |
| `services/api/src/main.ts` | starting and stopping the relay |
| `services/api/package.json` | the NATS client |
| `turbo.json` | the broker's env var for the integration lane |
| `packages/e2e/src/harness.ts` | forwarding the broker's address to the child api |

Seven amendments, plus whole-file fences for whatever the relay module contains and
the demonstration script. Roughly 12–15 fences — the size of a normal chapter,
because this chapter adds a path rather than retiring a seam. If implementation
finds more, that is a finding to record, not a surprise to absorb.

---

## R12 — Constitution VI, third time of asking

**Verified**: no coverage tooling and no CI exist in any of the three
repositories. Chapter 3.1 deferred the branch-coverage task; 3.2 deferred it by
explicit decision with the remedy scheduled "immediately after 3.2 and before
3.3".

**Status at the time of writing**: that feature has not run. If it does not run
before this chapter is implemented, this is the **third** chapter to ship
isolation- and durability-critical code without the measurement Principle VI
mandates — and this chapter's central claim is "no event is ever lost", which is
exactly the kind of claim a coverage bar exists to keep honest.

**This plan does not decide that.** It records the state and flags it in the
Constitution Check, where it belongs.
