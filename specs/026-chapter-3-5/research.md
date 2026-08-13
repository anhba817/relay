# Phase 0 — Research: Chapter 3.5, Webhooks That Survive the Customer

Checked against the repository at the `part3-ch4` state. Sources: `docs/04-srs.md`
(FR-WHK-01…09, FR-RTL-07, NFR-SEC-02/06/09, NFR-REL-08), `docs/05-sad.md` (§4.1's
dispatcher, §7's failure matrix, risk R5, risk R7), `docs/06-adr-deep-dives.md`
(ADR-01, ADR-02, ADR-04, ADR-06, ADR-15), the constitution (Principles I, II, IV,
V, VI, VII), chapter 3.4's research R5, and the current code.

---

## R1 — Where a pending retry lives  ✅ MEASURED AND RE-PLANNED 2026-08-10

**The requirement**: six attempts at roughly 1 s, 5 s, 30 s, 5 min, 30 min, 2 h
(FR-WHK-03), no retry earlier than its delay, the schedule surviving a restart of
the dispatching process (spec FR-023, SC-005), and one failing endpoint never
delaying deliveries to another (spec FR-020, SC-007).

**What that rules out immediately**: an in-process timer. A schedule stretching to
two hours cannot live in memory, and the dispatcher may not write a Postgres row to
persist it (constitution IV).

### The measurements

Run against the compose broker (nats:2.12-alpine) on 2026-08-10, before any code
was written.

**Q1 — does a delayed redelivery survive a restart of the consuming process?**
**Yes, to the millisecond.**

```text
process 1:  NAKKED  delay_ms=90000  at_epoch_ms=1786500140980  seq=1  delivered=1
            (process exits — it does not exist for the remainder of the test)
process 2:  ARRIVED at_epoch_ms=1786500230983  redeliveryCount=2
            expected 1786500230980 — late by 3 ms
```

The delay is server-side state on the consumer. A process that naks and then dies
has already handed the schedule to the broker.

**Q2 — do messages waiting out a long delay consume the outstanding-acknowledgement
budget?** **Yes. This is what re-planned the design.**

```text
consumer max_ack_pending=3, five messages published
fetched and nak'd with a 300 s delay:  3
fetched afterwards:                    0     <- nothing, though two are waiting
consumer: num_ack_pending=3  num_pending=2  num_waiting=0
```

Three messages sleeping off a delay hold every slot. Two more are available and
cannot be fetched. Scaled to production: a handful of endpoints failing into the
30-minute and 2-hour tiers occupy the dispatcher's whole budget and deliveries to
**healthy** endpoints stop — the exact failure FR-WHK-05 exists to prevent, and one
that is invisible until an incident, because the mechanism is flawless for one
endpoint and starves the system for many.

### The three candidates, judged against the measurement

| Candidate | Survives restart | Isolates failing endpoints | New machinery |
|---|---|---|---|
| **A.** nak-with-delay on one consumer | yes | **no — measured to starve** | none |
| **B.** nak-with-delay, one consumer per tier | yes | partly — starvation confined to a tier | six consumers, six budgets to size |
| **C.** a due-time row, drained when due | yes | **yes — nothing waits in the broker** | one table, one relay loop |

**A is eliminated by Q2.** It is the design the plan assumed and the measurement
disqualified it.

**B was the near-miss.** Partitioning the budget per tier keeps *initial* deliveries
flowing, which satisfies the letter of FR-WHK-05. But retries for healthy-ish
endpoints still queue behind dead ones inside a tier, thousands of messages still
sit in ack-pending for hours, and six budgets become six numbers nobody can size
from first principles. It trades a measured failure for an unmeasurable one.

**C is the decision.** A delivery that is not due yet is a row with a
`next_attempt_at`, not a message the broker is holding. Nothing occupies an
acknowledgement slot while it waits, so the isolation property is structural rather
than a function of tuning.

### Decision: the retry schedule is an outbox with a due time

**And that sentence is why this is the right answer for this book.** Chapter 3.3
built `SELECT … FOR UPDATE SKIP LOCKED`, publish, mark. Chapter 3.5 needs the same
loop with one extra predicate — `AND next_attempt_at <= now()`. The reader does not
learn a new mechanism; they discover that the one they already built generalises.

The pieces, and who owns them under constitution IV:

| Step | Where | Why there |
|---|---|---|
| Expand an event into N delivery rows | **api**, in the claim transaction | it is a database write; only the api may make one |
| Publish deliveries that are now due | **api**, a relay loop beside 3.3's | `drainOutbox`'s shape with a due-time predicate |
| Sign, POST, classify the outcome | **dispatcher** | SAD §4.1's job, and the part that must be starvable |
| Record the outcome, schedule the next attempt or dead-letter | **api**, one transaction | a database write, and the two must not diverge |

### What this buys beyond fixing the measured problem

**It removes a dual write the plan had accepted.** R2 originally expanded one event
into N *stream publishes* after claiming it — claim, then N publishes, with a crash
in between producing a partially-expanded event. As rows, expansion is one
transaction: the claim and all N deliveries commit together or not at all. The
"expansion runs exactly once" invariant stops needing care and becomes a property of
the database.

**It makes the retry schedule inspectable.** `next_attempt_at` is a column an
operator can query. A nak-delay is broker state nobody can see without asking the
consumer, which matters when the question is "why has this customer not received
anything for an hour".

### What it costs, stated plainly

One table (`webhook_deliveries`), one relay loop in the api, and **four more
fences** — `schedule.ts` and `delivery-relay.ts` as whole files, plus `main.ts` and
`app.module.ts` as amendments (R11). The chapter was already the series' largest and
this does not shrink it.

The honest counter-argument, recorded because it nearly won: candidate B needs no
new table and no new loop, and the tutorial's job is to teach rather than to build
the best possible dispatcher. What decides it is that B's weakness cannot be
demonstrated to a reader — "six budgets, sized by feel, and starvation confined to a
tier" is not a lesson — whereas C's mechanism is one the reader already owns, and
its correctness is visible in a `WHERE` clause.

### The dual write that remains, and why the chapter should say so

The dispatcher posts, then reports the outcome over the internal seam, then
acknowledges the stream message. A crash between the POST and the report means the
delivery is redelivered and posted again.

That is chapter 3.3's dual write, arriving for the **third** time — and the answer
is the one 3.3 and 3.4 already gave: accept it, and make the duplicate harmless. The
report is idempotent on `(delivery_id, attempt)`, so a redelivery after a successful
report is recognised and simply acknowledged; and the customer deduplicates on the
event `id` this chapter hands them (spec FR-018, invariant 16).

**The chapter should name the pattern rather than solve it a third time in silence.**
The dual write is not a bug that gets fixed; it is the standing cost of every hop
between two systems that cannot share a transaction, and it recurs at every such
hop. A reader who leaves this chapter expecting never to meet it again has learned
the wrong thing.

**Alternatives considered**: an external scheduler (rejected — a new dependency and a
new deployable for a problem two existing mechanisms already cover); keeping the
schedule in the broker via candidate B (rejected above, with its argument recorded).

---

## R2 — The retry unit is `(event, endpoint)`, not the event

**Verified against the requirement**: FR-WHK-01 allows several endpoints per
environment, each with its own subscription set. One `message.created` can
therefore match more than one endpoint.

**The bug this avoids**: if the retry unit were the event, a failure at one
endpoint would redeliver the event, and the dispatcher would post again to every
endpoint that had already succeeded. The customer sees duplicates caused by
somebody else's outage — a duplicate that no amount of consumer discipline on their
side can explain.

**Decision**: on receiving an event, expand it into one delivery per matching
endpoint, and give each delivery its own independent lifecycle. The expansion is
itself the thing that must not be repeated, which makes it the place the
3.4-style deduplication claim belongs (R5).

**Consequence — amended after R1's measurement**: an independently retryable unit
needs somewhere durable to sit between attempts, and that place is a **row**, not a
message the broker is holding. Each delivery is a `webhook_deliveries` row with its
own `next_attempt_at`; the api's relay publishes it to the deliveries stream only
when it is due, and the dispatcher consumes what is already due.

This is a simplification rather than a complication. The original plan expanded one
event into N *stream publishes* after claiming it — a claim followed by N publishes,
with a crash in between leaving an event partly expanded. As rows, the claim and all
N deliveries commit in **one transaction**. "Expansion runs exactly once" stops being
something the code must be careful about and becomes a property of the database.

**Alternatives considered**: keeping the event as the unit and tracking a
per-endpoint success set alongside it (rejected — it is the same state in a shape
where forgetting to consult it reintroduces the duplicate; the failure is silent
and lands on the customer).

---

## R3 — The signing secret cannot be hashed, and the resemblance to chapter 3.2 is the trap

**Verified**: NFR-SEC-02 says "API key secrets and webhook signing secrets shall be
stored only as salted hashes **or under envelope encryption**". Chapter 3.2 took the
first branch for API keys.

**Decision**: envelope encryption, because the second branch is the only one that
works here.

**The reason, stated because it is the chapter's best small lesson**: an API key is
*verified* — a caller presents it, the platform hashes what arrived and compares.
A webhook signing secret is *used* — the platform must compute an HMAC with it,
which requires the secret itself. A hash cannot be used, only compared. Two
credentials, one NFR, two mechanisms, and the reason is not "different security
levels" but "different verbs".

**Consequence**: the platform holds a decryptable customer credential for the first
time, which raises obligations chapter 3.2's hashes did not. The key that decrypts
it comes from configuration and never from the database — otherwise the encryption
is a filing convention rather than a protection. The plaintext exists only in
memory, only for the duration of a signature, and never in a log line
(NFR-SEC-06).

**Alternatives considered**: hashing it and having the *customer* send a signature
the platform verifies (rejected — inverts the protocol; the customer's endpoint is
the one that needs to authenticate the caller, not the other way round); asymmetric
signing with a published public key (rejected for this chapter — it solves the
"platform holds a usable secret" problem genuinely well, but FR-WHK-08 says
"signing secret" and shared-secret HMAC is what a customer's framework expects; it
is worth naming in the chapter as the thing a v2 would consider).

---

## R4 — The signature a customer can verify without asking

**Decision**: HMAC-SHA256 over a canonical string combining a timestamp and the
exact request body, sent in a header alongside the timestamp and a scheme version.

**The four properties the chapter must earn, not assert:**

| Property | How |
|---|---|
| Verifiable offline | everything needed is in the request plus the shared secret |
| Replay-resistant | the timestamp is inside the signed string, and recipients are told to reject old ones |
| Body-exact | signed over raw bytes, so re-serialising JSON before verifying is documented as the way to get it wrong |
| Upgradable | a scheme version in the header, so a future algorithm is not a breaking change |

**Rotation**: during a rotation window an endpoint has two valid secrets and the
delivery carries a signature for each. A recipient accepting either is correct
throughout; a recipient accepting only the newest is correct after the window. The
window is stated, in the chapter and in the contract.

**The test that matters**: the verifying side in the test suite must be written
independently of the signing code — its own HMAC, from the documented recipe. A
test that verifies with the signing function proves the function agrees with
itself, which is what a customer cannot do.

**Alternatives considered**: signing a digest of the body rather than the body
(rejected — one more step for a recipient to get wrong, no benefit at these
sizes); putting the signature in the body (rejected — it makes the body
self-referential and forces recipients to parse before verifying).

---

## R5 — Where 3.4's claim goes when it cannot join the effect

**The situation**: chapter 3.4's mechanism was a ledger claim and the effect in one
transaction. Here the effect is an HTTP request to another party's machine, and the
claim would be an internal call to another service. They cannot share a
transaction, and no arrangement of them can be made atomic.

**Decision**: split the problem where it actually splits.

- **Expansion is claimed.** Turning one event into N deliveries is a database write
  behind the internal seam, so it can reuse 3.4's exact mechanism — claim and
  effect in one transaction, inside the api. An event expanded twice would double
  every webhook, so this is where deduplication earns its keep.
- **Delivery is not claimed; it is recorded.** The POST happens, then its outcome is
  reported. If the report fails after a successful POST, the redelivery posts again
  and the customer sees a duplicate. That is the accepted failure, and FR-003
  requires the chapter to say so and hand over the event identifier that absorbs
  it.

**Why not claim before posting**: claiming first turns the terminal hop
at-most-once — a crash between the claim and the POST loses the webhook silently,
which is the failure chapter 3.3 spent itself removing. Given a choice between a
duplicate the customer can deduplicate and a loss they cannot detect, the platform
takes the duplicate. **That sentence is the chapter.**

---

## R6 — What the dispatcher authenticates as

**Verified**: the api's internal routes sit behind `CredentialGuard`, and the
credential model has exactly two principals — `application` (an API key, chapter
3.2) and `user` (an end-user token). The gateway forwards a tenant's credential
because it acts on behalf of that tenant.

**The dispatcher does not.** It acts on behalf of the platform, across every
environment at once — the same posture the outbox relay and the 3.4 consumer have
inside the api, where the repository calls it an "admin surface". It is the first
caller to hold that posture *from outside the process*, and the credential model
has no shape for it.

**Decision**: a third principal kind for platform-internal callers, carried by a
credential that is configuration rather than tenant data, and accepted **only** on
internal routes — never on a public one. The guard's existing `Accepts` mechanism
already expresses the restriction; what is missing is the kind.

**The trap to write down**: the obvious shortcut is to mint the dispatcher an API
key. It would work immediately and it would be wrong — an `application` principal
is scoped to one environment by construction (3.1, 3.2), so a dispatcher holding
one either cannot serve other tenants or has been quietly granted cross-tenant
reach through a credential type whose whole meaning is that it does not have any.
Principle I is a correctness property; this is exactly where it would be eroded by
convenience.

**Alternatives considered**: network-level trust with no credential (rejected — the
internal seam is one misconfigured ingress from being external, which chapter 2.5
already argued when it validated internal payloads); mutual TLS (rejected for this
chapter — a real answer, and a certificate lifecycle this platform has no story for
yet; named as the thing a production deployment adds).

---

## R7 — One slow customer must not become everyone's problem

**The requirement**: FR-WHK-05 — delivery must never delay message delivery to end
users — plus spec FR-020, that one slow endpoint must not delay deliveries to
others.

**Decision**: a per-attempt timeout, and a bound on how many attempts may be in
flight for any single endpoint, so a hanging customer consumes a fixed and small
share of the dispatcher.

**Why the service split does most of this work already**: the strongest guarantee
against webhooks delaying message delivery is that the code posting to customers
runs in a process that shares nothing with the write path. Inside the api, "does
not delay end users" would be a claim about event loops and connection pools;
across a process boundary it is a claim about processes. The chapter should show
this rather than assert it — stopping the dispatcher entirely and watching message
delivery continue is a two-line demonstration and a better argument than a
paragraph (SC-009).

**The number the chapter must not dodge**: the timeout is a decision with a cost in
both directions — too short and a slow-but-working customer is failed unfairly,
too long and a hanging endpoint holds a slot. State it with its reasoning, as 3.4
stated its acknowledgement deadline.

---

## R8 — The dead-letter store is not like the last two tables

**Verified**: FR-WHK-04 — exhausted events are retained for 7 days, inspectable and
replayable.

**Decision**: tenant-scoped, with `environment_id`, behind the repository layer.

**The rule this settles.** Chapters 3.3 and 3.4 each added a table with no
`environment_id` and each recorded it as a deliberate exception: the outbox and the
consumed-events ledger are work the platform owes itself, read by one process on
behalf of nobody. Two exceptions in consecutive chapters is a pattern, and a
pattern needs a stated rule before a third chapter judges by resemblance.

**The rule**: a table is exempt from tenant scoping when it holds the platform's
own bookkeeping and no tenant-visible content. A dead letter holds a payload that
was being sent to a customer, so it fails the test on both halves. It is tenant
data that happens to live in an operational table, and it joins chapter 3.7's
cross-tenant gauntlet as a target like any other.

**Retention as a liability, not a feature**: this is the first store whose purpose
is retaining data that failed to leave. Seven days is FR-WHK-04's number; the
chapter should say what happens on day eight and mean it, because a dead-letter
table with no expiry is a place tenant data accumulates until somebody notices it
in an audit.

---

## R9 — Posting to a URL a customer chose

**The exposure**: the dispatcher makes outbound requests to addresses supplied by
tenants. Left unguarded that is a request-forgery primitive pointed at whatever the
dispatcher can reach.

**Decision**: validate at configuration time — require HTTPS, and reject loopback,
link-local and private ranges — and state the check in the chapter. No source
requirement mandates this, so it carries a `DECISION` note (spec FR-008).

**Deliberately not built**: DNS re-resolution at delivery time to defeat rebinding,
an egress proxy, an allowlist. Each is a real hardening step and each needs
infrastructure this platform does not have; naming them honestly is better than
implying the simple check is complete. NFR-SEC-07's OWASP scan is where this comes
back.

**What the service split buys here**: an outbound fetch to a customer-controlled
URL now happens in a process that holds no database credential. That is a real
security dividend of the decision and worth one sentence in the chapter, because
architecture decisions that pay off in more than one dimension are the ones worth
teaching.

---

## R10 — The dependency budget: zero

**Verified against the workspace**: the four things this chapter needs are all
already present or built in.

| Need | Supplied by |
|---|---|
| Outbound HTTP | Node 22's global `fetch` |
| HMAC-SHA256 | `node:crypto` |
| AES-GCM for the secret at rest | `node:crypto` |
| JetStream | `nats@2.29.3`, since 3.3 |

**Decision: add nothing.** A chapter that introduces a deployable service and no
dependency is worth pointing at, given Principle VII — and given that the obvious
reflex when starting a new service is to reach for a framework, an HTTP client and
a retry library before writing a line of it.

**Related, from ADR-15**: the dispatcher is frameworkless. NestJS is bound to the
API service *only*; a second Nest application would be adopting a framework by
momentum. The gateway has been frameworkless since Part 1 and is the shape to copy.

---

## R13 — The api's second relay loop (added by R1's re-plan)

**Decision**: the api gains a delivery relay beside chapter 3.3's outbox relay —
`SELECT … FOR UPDATE SKIP LOCKED` over `webhook_deliveries` where
`next_attempt_at <= now()`, publish each to the deliveries stream, mark dispatched.

**Verified reusable**: 3.3 shipped `drainOutbox(db, limit, publish)` — a transaction
that claims rows with `SKIP LOCKED`, hands each to a `publish` callback, and marks
them — driven by `createRelay({ drainOnce, intervalMs })`, a loop with an idle
interval and explicit start/stop. Both are shaped for exactly this second use: the
new drain differs by one predicate and one table.

**Why this belongs in the api and not the dispatcher**: constitution IV. Reading
which deliveries are due is a database read, and the dispatcher may not make one.
Putting the scheduler where the data lives also means the "schedule the next attempt"
write happens in the same transaction as "record this attempt's outcome", so the two
can never disagree.

**Consequence for the chapter**: the api now runs two relays. That is worth a
paragraph rather than a footnote — it is the moment the reader sees that the outbox
pattern was not a one-off for events but a general shape for *any* work the platform
owes itself and must not lose. The second instance is what makes it a pattern.

**Consequence for the tests**: suites that want a quiet database must be able to
silence this loop as they already silence 3.3's. `RELAY_OUTBOX_RELAY=off` has a
sibling, and chapter 3.3's finding 4 — that a background daemon and a test lane do
not share a table quietly — applies again, in advance this time.

**Alternatives considered**: folding the due-delivery drain into 3.3's existing relay
(rejected — one loop draining two tables couples the event spine's latency to webhook
retry volume, and the two have different tuning); a database trigger or `LISTEN`/
`NOTIFY` to wake the relay when a delivery falls due (rejected for the reason 3.3's
R2 rejected it — an optimisation on a budget with orders of magnitude of headroom,
and the poll must exist anyway as the correctness path).

---

## R11 — The fence budget, costed before rather than after

**Amendments to files earlier chapters have fenced:**

| File | Why it changes |
|---|---|
| `services/api/src/db/schema.ts` | **three** tables — endpoints, deliveries, dead letters |
| `services/api/src/db/repository.ts` | scoped endpoint ops, expansion, `drainDueDeliveries`, `recordAttemptOutcome` |
| `services/api/src/main.ts` | starting and stopping the delivery relay (R13) |
| `services/api/src/app.module.ts` | the webhooks module and the relay |
| `packages/protocol/src/internal.ts` | the dispatch contract schemas |
| `packages/e2e/src/harness.ts` | forwarding the dispatcher's env to the child api |
| `services/api/src/auth/principal.ts` | the third principal kind (R6) |
| `services/api/src/auth/credential.guard.ts` | accepting it on internal routes only |
| `services/api/src/internal/internal.module.ts` | the dispatch controller |
| `compose.yaml` | the dispatcher |
| `turbo.json` | its tasks and env |
| `vitest.coverage.config.mts` | its coverage surface |
| `.github/workflows/ci.yml` | its CI job |

Thirteen amendments — more than any previous chapter, and three of them added by
R1's re-plan — plus whole-file fences for the migration, the api's `webhooks/`
module (including `schedule.ts` and `delivery-relay.ts`), the dispatch controller,
the dispatcher service's own files, and two scripts.

**Budget: 22–26 → 25–29 (R1's re-plan) → 37–41 (this revision).** Two corrections,
both of which the earlier numbers got wrong:

**Test files count, and were never counted.** Chapter 3.4 fenced
`consumer.itest.ts` inside its 15–18 budget, and spec FR-029 — added *because* 3.4
left two test files unfenced — requires every file the prose asserts to be fenced.
This chapter creates **seven**: `secret.test.ts`, `webhooks.itest.ts`,
`deliveries.itest.ts`, `signature.test.ts`, `dispatcher.itest.ts`,
`credentials.itest.ts`, `e2e/webhooks.itest.ts`. Omitting them made the old ceiling
unreachable: 13 amendments + 16 new files already summed to 29 exactly, *before* a
single test.

**Containerisation adds four** (author's decision, 2026-08-10): Dockerfiles for the
api, the gateway and the dispatcher, plus a `.dockerignore`. The repository has
never had one.

Running total: 13 amendments + 16 new + 7 tests + 4 container files = **40**.

**Note the tier table's home.** `schedule.ts` lives in the **api**, not the
dispatcher: the tiers are read by `recordAttemptOutcome` when it computes the next
`next_attempt_at`, and that is a database write only the api may make (constitution
IV). Putting them in the dispatcher would look natural and be wrong.

For comparison: 3.3 budgeted 12–15 and shipped 19; 3.4 budgeted 15–18 and shipped
17, the first to land inside its estimate. This is by a wide margin the largest
chapter in the series and the budget should be treated as a warning rather than an
estimate — if implementation approaches 29, that is the signal to check whether the
narrowing decision held, not to absorb the overrun.

**The re-plan made the chapter bigger, and that is the honest trade**: candidate B
would have cost nothing here. What the extra three fences buy is an isolation
property that holds structurally instead of by tuning, one fewer dual write, and a
mechanism the reader already owns from chapter 3.3.

---

## R12 — Constitution VI, and the way a new service quietly escapes it

**Verified**: feature 024's `vitest.coverage.config.mts` includes
`packages/*/src/**` and `services/*/src/**`, and its per-file ratchets name files
that existed when it was written. `.github/workflows/ci.yml` runs the platform's
gates from the parent repository.

**The failure mode**: a new deployable added without touching either file sits
outside the measurement. Every existing ratchet stays green, the coverage summary
reports a comfortable number, and none of it covers the service that posts tenant
data to the internet. An instrument reporting confidently about the wrong scope is
worse than no instrument, because the first produces a decision.

**Decision**: extending coverage and CI to the dispatcher is part of the task that
creates it, not a follow-up — and the chapter states the general form, because
every later service in this series will meet the same trap.

**Where the ratchets will move**: `repository.ts` gains scoped endpoint and
dead-letter operations, and it currently sits at 86.30% branches against a ratchet
of 85 (chapter 3.4, research R10). The margin is thin. Expect to raise the ratchet
with this chapter's work rather than to discover it broken at the end.
