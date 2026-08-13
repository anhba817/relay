# Phase 1 — Contracts: Chapter 3.5, the internal seam

The dispatcher owns no database. Constitution IV: "Only the API service writes to
PostgreSQL… Other services obtain writes and backfill reads via the API service's
internal endpoints."

This is the second service to live under that rule. The gateway has since chapter
2.5, and the shape is deliberately the same: an `api-client.ts` that is the only
road to state, request and response schemas in `@relay/protocol` so the two sides
cannot drift, and responses **parsed rather than assumed**.

---

## What the dispatcher may ask for

| Operation | Why it exists |
|---|---|
| Expand an event into deliveries | one event, N matching endpoints — a claimed write producing N rows in one transaction (research R2, R5) |
| Fetch an endpoint's delivery material | URL, subscriptions, and the decrypted signing secret(s) for the rotation window |
| Report an attempt's outcome | delivered, or failed-and-rescheduled, or exhausted-and-dead-lettered |

**Expansion is a claim, not a read.** It reuses chapter 3.4's mechanism unchanged —
the ledger row and the effect in one transaction, inside the API service, where a
transaction is possible. Since R1's re-plan the "effect" is *N rows in
`webhook_deliveries`*, so the claim and every delivery it produces commit together
or not at all. An event expanded twice doubles every webhook it produced, and this
is now prevented by the database rather than by care.

**Reporting an outcome is not a claim — it is idempotent.** The POST already
happened on somebody else's machine and cannot be undone. The report is keyed on
`(delivery_id, attempt)`, so a redelivery arriving after a successful report is
recognised and simply acknowledged rather than posted again.

**What the API service does inside that report, in one transaction**: record the
outcome, and either mark the delivery `delivered`, or compute the next tier and set
`next_attempt_at`, or move it to the dead-letter store. Splitting those would allow
a delivery marked failed with no next attempt scheduled — a webhook that stops
without anyone being told.

**The dual write that remains.** Between the POST and the report there is a gap, and
a crash in it means the delivery is redelivered and posted twice. That is chapter
3.3's dual write arriving a third time; the answer is the one 3.3 and 3.4 gave —
accept it, and make the duplicate harmless via the event `id` (invariant 16). The
chapter should name the pattern rather than quietly solve it again: **the dual write
is the standing cost of every hop between systems that cannot share a transaction.**

### The secret crosses a process boundary

Fetching delivery material returns a **decrypted** signing secret, because the
dispatcher is what signs (SAD §4.1). That is a real widening of where a customer
credential exists and the chapter must not skip past it.

| Obligation | |
|---|---|
| Internal network only | never reachable from a public route |
| Never logged | not the secret, not the material response, at any level (NFR-SEC-06) |
| Held for the signature only | not cached beyond a short, stated lifetime |
| Never in an error | a failed delivery reports status and error text, never what it was signed with |

**The alternative that was considered**: the API service signs and the dispatcher
posts an opaque body. It keeps the secret in one process, and it makes the API
service do per-delivery crypto on behalf of a service that exists to absorb that
work. SAD §4.1 puts signing in the dispatcher; the chapter states the trade rather
than pretending there is no cost.

---

## Authentication

The dispatcher presents a **`platform`** principal — the third kind, added by this
chapter (research R6, data-model §The credential model).

| Rule | |
|---|---|
| Accepted on internal routes only | never on a public route, enforced by the guard's opt-in |
| Credential is configuration | not tenant data, not an API key |
| Reaches every environment | which is exactly why it may never be accepted publicly |

**Not an API key.** An `application` principal is scoped to one environment by
construction. A dispatcher holding one either cannot serve other tenants or has
been granted cross-tenant reach through the credential type whose entire meaning is
that it has none.

---

## Failure between the services

| Situation | Behaviour |
|---|---|
| API service unreachable | the dispatcher stops making progress and retries; nothing is lost, because the stream holds the work |
| Dispatcher absent entirely | **the API service is unaffected** — messages are delivered, events accumulate, the backlog drains on return (spec FR-016, SC-009) |
| Outcome report fails after a successful POST | redelivery re-posts; the customer deduplicates on `id` |
| Endpoint deleted mid-flight | in-flight deliveries stop; nothing accumulates for a destination that no longer exists |

**The direction of that dependency is the point.** The dispatcher needs the API
service; the API service needs nothing from the dispatcher. An event spine whose
consumer can take down the write path would have inverted the dependency chapter
3.3's outbox exists to remove.

---

## Invariants the tests must hold

Sixteen. Two are pure and live in the Docker-free lane; the rest need the stores,
the broker, or a hostile endpoint that fails on command.

| # | Invariant | Requirement | Lane |
|---|---|---|---|
| 1 | An environment cannot configure more endpoints than the limit, and the error names it | FR-WHK-01, spec FR-009 | integration |
| 2 | A created secret is returned once and never again by any read | spec FR-010 | integration |
| 3 | No environment can observe or affect another's endpoints | constitution I, spec FR-011 | integration |
| 4 | A delivery's signature verifies against an **independently written** verifier | spec FR-017, SC-002 | **unit** |
| 5 | Re-serialising the body before verifying fails — the documented trap, asserted | contracts §Verifying | **unit** |
| 6 | During a rotation window both secrets verify; after it, only the new one | spec FR-010, SC-002 | integration |
| 7 | An endpoint receives only its subscribed event types | spec FR-021, SC-008 | integration |
| 8 | One event matching N endpoints produces N delivery rows **in one transaction**, and expansion runs once however often the event is redelivered | research R2, R5 | integration |
| 9 | A failing endpoint is attempted exactly six times, each attempt's `next_attempt_at` matching its tier | FR-WHK-03, SC-003 | integration |
| 10 | No delivery is published before `next_attempt_at`, and a not-yet-due delivery occupies no acknowledgement slot | spec FR-023, SC-004, research R1 | integration |
| 11 | A pending retry survives a restart of **both** the dispatcher and the api — the schedule is a row, so neither process holds it | spec FR-023, **SC-005** | integration |
| 12 | An exhausted delivery is dead-lettered, retrievable, and replayable with its original event id | FR-WHK-04, SC-006 | integration |
| 13 | A hanging endpoint is abandoned on the timeout and does not delay deliveries to others | FR-WHK-05, spec FR-020, SC-007 | integration |
| 14 | With the dispatcher stopped, messages are delivered normally and the backlog drains on return | spec FR-016, SC-009 | integration |
| 15 | No dispatcher log line contains a signing secret or a tenant's message body — at any level, including error paths | spec FR-025, SC-011, NFR-SEC-06 | integration |
| 16 | A delivered body is chapter 3.3's envelope and carries the event `id` a recipient deduplicates on | spec FR-018, contracts/webhooks.md | integration |

**On 4 and 5.** These are pure because a signature is a pure function of a secret, a
timestamp and some bytes — and they are the two that matter most to a customer.
Invariant 4 must use a verifier written from the documented recipe, **not** the
signing code: a test that verifies with the signing function proves the function
agrees with itself, which is the one thing a customer cannot rely on.

**On 11.** This is the invariant that decided the design, and R1's measurement is
why it reads as it does. A broker-held delay was measured durable to the
millisecond — and fatal in aggregate, because messages waiting out long delays hold
acknowledgement slots, so a handful of dead endpoints starve deliveries to healthy
ones. The schedule is therefore a `next_attempt_at` column, and this invariant now
restarts **both** processes, because a row is held by neither.

**On 10's second clause.** "Occupies no acknowledgement slot" is the assertion that
would have caught the original design. It is not a performance check — it is the
isolation property FR-WHK-05 asks for, expressed in the one place it can be
observed.

**On 15.** Chapter 3.4 carried this invariant and 3.5 must not be the chapter that
quietly drops it — this one handles a *decryptable customer credential*, which 3.4
never did. NFR-SEC-06 is a MUST and Principle VI requires it be test-verified, so a
scan of the captured transcript is not sufficient: the assertion belongs against the
running service's own log output, including the error paths, which are exactly where
a secret gets printed by accident.

**On 16.** The event `id` in the delivered body is the entire mechanism by which a
customer absorbs the duplicate the platform has chosen to send them (FR-003). It is
implied by "the body is the 3.3 envelope" and implication is not a test — if it ever
went missing, every claim the chapter makes about at-least-once being survivable
would become false at the only hop a customer can see.

**Sabotage check**: signing over the parsed-and-re-serialised body instead of the
raw bytes must fail invariants 4 and 5. Expanding the event without claiming it must
fail invariant 8. Publishing deliveries regardless of `next_attempt_at` must fail
invariants 9 and 10. Logging the delivery-material response must fail invariant 15.
A suite that passes with any of those mechanisms removed is holding nothing.
