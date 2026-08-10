# Phase 0 — Research: Chapter 3.4, JetStream and the First Consumer

Checked against the repository at the `part3-ch3` state (plus feature 024's
coverage tooling and CI). Sources: `docs/04-srs.md` (FR-WHK-02/03/04, FR-ANL-06,
FR-MSG-03, NFR-REL-08, NFR-SEC-06), `docs/05-sad.md` (§6.1's `outbox`, §7's
failure matrix, risk R5), `docs/06-adr-deep-dives.md` (ADR-02, ADR-04, ADR-06,
ADR-16), the constitution (Principles II, III, IV, VI, VII), and the current
code.

> **Reconstruction note.** R1 and R4 were measured against a live broker during
> implementation; those transcripts were lost with the machine. The findings
> below are recovered from the chapter's prose and from the code they produced —
> both of which state the measured result explicitly — and are marked
> `MEASURED (recovered)` rather than `MEASURED`. R10 was re-measured on
> 2026-08-10 and carries today's numbers. Everything else is a design decision
> whose reasoning survives in the fenced comments.

---

## R1 — Which stream settings can be changed after creation

**MEASURED (recovered).** `retention` and `storage` are immutable on an existing
stream. The broker refuses a change to either with an error; it does not
reconcile the difference or silently keep the old value.

**Decision**: `ensureStream` splits the configuration in two. The mutable
settings are merged onto whatever the stream currently has; the immutable ones
are supplied only on the create path and carried through untouched on the update
path.

**Why it matters more than it looks**: chapter 3.3 created this stream as "the
minimum a publisher needs", and two of the three settings it chose by hand happen
to be the two that can never be changed. Had 3.3 taken memory storage as a
development convenience, applying this chapter's configuration would have meant
deleting the stream and every event in it. That is worth saying out loud in a
tutorial: the settings you are least likely to think about at creation time are
the ones you are least able to fix later.

**Alternatives considered**: delete-and-recreate on a configuration mismatch
(rejected — it discards the event history the previous chapter spent itself
proving durable); refusing to run against an existing stream at all (rejected —
two api instances start together, so the second must find a stream that exists
and proceed).

---

## R2 — The inherited defaults, and every setting as a decision

**Verified**: at `part3-ch3` the `EVENTS` stream reported `max_age 0` (no limit),
`max_bytes -1` (unbounded), `discard old`, `duplicate_window 120s`, and
`num_replicas 1`. Three settings were chosen by chapter 3.3 — the name, the
subject list, and file storage. The rest are whatever NATS does when you do not
say.

**Decision**: every setting becomes a decision with a reason attached.

| Setting | Value | Reason |
|---|---|---|
| `max_age` | 7 days | NFR-REL-08 asks for ≥ 24 h. The floor protects a process crash; a week protects a Friday-evening outage nobody notices until Monday. |
| `max_bytes` | 1 GiB | An unbounded stream fills the disk the database is on. A bound that stops the event spine is preferable to one that stops the write path. |
| `discard` | `old` | At the bound, drop the oldest. The alternative refuses new publishes, which would take the write path down with the event spine — the inversion 3.3's outbox exists to prevent. |
| `duplicate_window` | left at 120 s | See R3. Raising it looks like the fix and is not. |
| `num_replicas` | environment-derived | See R11 below — ADR-02 specifies R3, the compose stack is one node. |

**Rationale**: a default is not paid for when you take it. It is paid for the
first time it matters, which is usually an incident. The chapter's argument is
that the audit is cheap now and expensive later.

---

## R3 — The broker's duplicate window is not the deduplication guarantee

**Decision**: leave `duplicate_window` where chapter 3.3 found it, and put the
guarantee at the consumer.

**Rationale**: the broker's window dedupes *publishes* within a bounded time. The
outbox can republish hours after an outage — that is precisely the at-least-once
behaviour 3.3 embraced — so no window is a safe guess about the longest gap. And
a window measured in hours would hold that dedupe index in the broker's memory
for hours, which is a real cost paid for a guarantee that still would not hold.

SAD risk R5 asks for the behaviour, not the mechanism: "a future consumer forgets
to dedupe → double webhooks / double metering", mitigated by "a consumer template
with dedup built in". A broker setting cannot be that template. A ledger row
written in the same transaction as the effect can.

**Alternatives considered**: raising the window to cover the worst observed
outage (rejected as above — it is a guess that fails silently when wrong).

---

## R4 — What happens when delivery attempts are exhausted

**MEASURED (recovered).** With `max_deliver` bounded, a message whose handler
throws on every attempt stops being delivered and **leaves the consumer's view
entirely**. Nothing catches it. There is no dead-letter subject, no holding
stream, and no log line from the broker that a consumer sees.

**Decision**: bound the attempts at 5 and say plainly in the chapter that nothing
catches what falls out.

**Rationale**: forever is not a retry policy — an unbounded retry turns one
poison message into a consumer that never advances. But a bound without a
dead-letter store means messages can be lost after repeated failure, and that is
the kind of thing a tutorial is tempted to imply it has solved. FR-WHK-04's
dead-letter store belongs to chapter 3.5. This chapter states the gap.

**Consequence for the tests**: invariant 7 asserts the exhaustion behaviour
rather than the absence of a dead letter, so it will not need rewriting when 3.5
adds one.

---

## R5 — Where the consumer runs, and what that costs chapter 3.5

**Decision**: inside the api service, started with the application and stopped
with it — the same placement ADR-06 chose for the outbox relay, for the same
reason.

**The cost, named rather than discovered**: the ledger claim and the handler's
effect share a transaction because both are in Postgres, and the consumer can
open that transaction because it runs inside the service that owns the database.
Chapter 3.5's webhook dispatcher is meant to be its own service. When it moves
out, it will need either an internal route for its ledger or an explicit ADR
amendment — and its effect is an HTTP call to a customer, which cannot be rolled
back by any transaction. That consumer must choose which way to be wrong.

**Consequence for tests**: the consumer must be startable and stoppable
independently of request handling, so suites that want a quiet broker simply do
not start it. `RELAY_EVENT_CONSUMER` is the switch, on by default — an event
spine nobody reads is what 3.3 left behind.

---

## R6 — Pull over push, and the shape of a fetch

**Decision**: a durable **pull** consumer, fetching bounded batches, with
back-pressure on outstanding acknowledgements.

**Rationale**: a push consumer hands work to the client at the broker's pace,
which means a slow handler accumulates unacknowledged messages it never asked
for. A pull consumer asks for work when it is ready for work, so the natural
back-pressure is "do not ask", and the acknowledgement deadline is never held
over a batch the handler has not started.

**The numbers, with reasons rather than defaults**: a batch small enough that a
slow handler does not hold an acknowledgement deadline over a hundred messages,
and large enough that a backlog of twelve thousand drains in sensible steps
rather than one round trip each; a bound on outstanding acknowledgements so a
stalled consumer cannot accumulate an unbounded pile.

---

## R7 — Proving the consumer's gap

**Decision**: a child process, killed by the parent with `SIGKILL` at a marker it
prints between committing the effect and acknowledging the message. The same
shape chapter 3.3 used for the dual-write demonstration.

**Rationale**: the property under test is "what survives when the process stops
existing". A test that throws an exception proves the code's own error path,
which a real signal never reaches. 3.3 established this discipline for
durability; 3.4 applies it one hop further along.

**The setting this constrains**: the acknowledgement wait must be long enough for
a real handler and short enough that a killed instance's work comes back
promptly — which is also what makes the redelivery test tolerable to run rather
than a suite nobody waits for.

**And one artifact, not two**: the walk script the test kills is the same script
a reader runs by hand. Neither can rot without the other noticing — the same
argument 3.3 made for `dual-write-walk.mjs`.

---

## R8 — The durable name is a position, not a process

**Verified**: a durable consumer is a cursor the broker maintains on the
consumer's behalf. Every instance using the same durable name shares that one
position.

**Decision**: create the durable if absent, leave it alone if present.

**Consequence**: two api processes started together divide the stream between
them rather than each receiving every event — which is the ordinary deployment,
not an edge case, because the api is stateless and runs more than once. It also
means a consumer that assembles its own subject filter is a consumer that
silently receives nothing the day the grammar changes: no error, no warning, just
an empty position. That is why R12's subject grammar moves to the shared package.

---

## R9 — The subject grammar belongs to both sides

**Verified**: `subjectFor` lived inside the api's outbox module since 3.3,
because nothing else needed it.

**Decision**: move it to `@relay/protocol` and re-export from its old home so
3.3's callers keep working.

**Rationale**: chapter 1.3's premise is that the package whose whole job is the
shapes both sides share is where a shape shared by both sides belongs. A consumer
needs the grammar now. Built in one place and nowhere else, because the failure
mode of a duplicated grammar is silent — a filter that matches nothing looks
exactly like a stream with nothing in it.

---

## R10 — Constitution VI, measurable at last

**Verified**: feature 024 landed coverage tooling (`vitest.coverage.config.mts`,
both lanes, real stores) and CI (`.github/workflows/ci.yml` in the parent
repository, the only tree where all three exist at once). Chapters 3.1, 3.2 and
3.3 each deferred this measurement; 3.4 is the first Part 3 chapter that can take
it.

**MEASURED (2026-08-10, both lanes against the compose stores):**

| Scope | Statements | Branches | At 024 |
|---|---|---|---|
| Workspace | **88.22%** (809/917) | **79.01%** (369/467) | 86.55% / 78.07% |
| `services/api/src/consumer/` (new) | 93.50% | 86.11% | — |
| `services/api/src/db/repository.ts` | 96.18% | **86.30%** | 85.91% |

**The finding that matters**: 024 pinned a per-file ratchet on `repository.ts` at
85% branches — deliberately below the 100% NFR-MNT-02 asks for, to stop the
figure sliding while the gap is closed. This chapter adds `claimEvent` and
`timesHandled` to that file, which is exactly the kind of change that quietly
breaks a ratchet. It does not: branches move **up**, 85.91% → 86.30%, and the
coverage run exits 0.

**What is still unmet**: NFR-MNT-02's 100% branch coverage for ordering,
idempotency and isolation code. `repository.ts` holds all three and measures
86.30%. The instrument now exists and the number is sayable; closing the gap
remains the work 024's notes describe.

---

## R11 — Replication, derived rather than chosen

**Verified**: ADR-02 specifies R3 replication. The compose stack is a single
node, which cannot satisfy it.

**Decision**: derive the replica count from the environment — an explicit
override if set, otherwise 3 in production and 1 elsewhere.

**Rationale**: a chapter that hardcoded `3` would not run locally, and one that
hardcoded `1` would ship a single-replica event spine to production. Neither is a
decision; both are an accident waiting for a different environment. This is the
one stream setting where the right value genuinely depends on where the code is
running, and saying so in code is cheaper than saying so in a runbook.

---

## R12 — The fence budget

**Files this chapter was expected to touch that earlier chapters have already
fenced:**

| File | Why it changes |
|---|---|
| `services/api/src/outbox/jetstream.publisher.ts` | every stream setting becomes a decision |
| `packages/protocol/src/internal.ts` | the subject grammar moves here (R9) |
| `services/api/src/outbox/event.ts` | the grammar's old home, now re-exporting |
| `services/api/src/db/schema.ts` | the ledger table |
| `services/api/src/db/repository.ts` | `claimEvent`, `timesHandled` |
| `services/api/src/main.ts` | starting and stopping the consumer |
| `services/api/src/app.module.ts` | the consumer module |
| `turbo.json` | two env vars for the lanes |
| `packages/e2e/src/harness.ts` | forwarding them to the child api |

Nine amendments, plus whole-file fences for the consumer module, the migration
and the two scripts. **Budget: 15–18.** Actual: **17** — the first Part 3 chapter
to land inside its budget (3.3 budgeted 12–15 and shipped 19).

The budget is right for a reason worth recording: unlike 3.3, this chapter
touches no service beyond the api and fixes forward into no earlier chapter. It
adds a reader to a path that already exists.
