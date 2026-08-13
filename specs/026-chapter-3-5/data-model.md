# Phase 1 — Data Model: Chapter 3.5

Three new tables, one amended credential model, one new stream, and one shape that
exists only on the wire — the request a customer's server receives.

All three carry `environment_id`. That is a change of direction from the last two
chapters and the reason is below.

---

## The rule the last two chapters were exceptions to

Chapter 3.3 added `outbox` with no `environment_id`. Chapter 3.4 added
`consumed_events` with none either. Both recorded the omission as a deliberate
exception. Two exceptions in consecutive chapters is a pattern, and a pattern
without a stated rule is how a third chapter gets it wrong by resemblance.

**The rule**: a table below the tenant boundary may omit `environment_id` only when
it holds the platform's own bookkeeping **and** no tenant-visible content. The
outbox holds work the platform owes itself; the consumed-events ledger holds the
fact that a consumer ran. Neither is anything a customer could be shown.

All three tables in this chapter fail that test — one is customer configuration,
one is work bound for a customer, one holds a payload that was being sent to a
customer — so all three are scoped, all three go through the repository layer's
environment-bound constructors, and all three join chapter 3.7's cross-tenant
gauntlet as targets.

---

## `webhook_endpoints` (new — derived)

| Column | Notes |
|---|---|
| `id` | endpoint identity, external-safe |
| `environment_id` | **required**, the tenant boundary (FR-TEN-06) |
| `url` | validated at write time: HTTPS, no loopback/link-local/private ranges (research R9) |
| `event_types` | the subscription set; an endpoint receives only these (spec FR-021) |
| `secret_ciphertext` | the signing secret under envelope encryption (research R3) |
| `secret_previous_ciphertext` | the outgoing secret during a rotation window |
| `secret_rotated_at` | when the window opened; both secrets sign until it closes **24 hours later** (contracts/webhooks.md §Rotation) |
| `enabled` | an owner can pause an endpoint; **what disables one automatically is the follow-on chapter's** |
| `deleted_at` | **deletion is soft.** A hard delete would have to cascade, and cascading would erase the customer's dead letters — which FR-WHK-04 says to retain for seven days. Chapter 3.2 reached the same conclusion for `api_keys.revoked_at` |
| `created_at` | |

No source document defines this table. FR-WHK-01 and FR-WHK-08 require the
behaviour and leave the shape open, so this is a chapter derivation and carries a
`DECISION` in `schema.ts`, as `members` (2.1), `api_keys` (3.2), the outbox index
(3.3) and `consumed_events` (3.4) each did.

**Rules**

- **At most five per environment** (FR-WHK-01). The limit is enforced at the write,
  and exceeding it is refused with an error that names the limit rather than a
  generic rejection.
- **The secret is never returned after creation.** It is shown once, at creation or
  rotation, and thereafter the platform can use it but not display it. This differs
  from chapter 3.2's API keys only in that the platform *can* recover it — which is
  precisely why the discipline has to be explicit rather than enforced by a hash.
- **The decryption key is configuration, never a database row.** A key stored beside
  the ciphertext it protects is a filing convention, not encryption.
- **Two secrets are valid during a rotation window**, and a delivery in that window
  carries a signature for each (contracts §Rotation).

---

## `webhook_deliveries` (new — derived, added by R1's re-plan)

One row per `(event, endpoint)` pair. This is the retry schedule, and it is
chapter 3.3's outbox with one extra column.

| Column | Notes |
|---|---|
| `id` | delivery identity; with `attempt`, the idempotency key for outcome reports |
| `environment_id` | **required** — tenant data (rule above) |
| `endpoint_id` | which endpoint this is bound for |
| `event_id` | chapter 3.3's envelope id — the customer's deduplication key, stable across every attempt and across a replay |
| `payload` | the envelope as it will be sent |
| `attempt` | 1…7; the tier index, not a free-running counter. The initial delivery plus FR-WHK-03's six retries — see `webhooks/schedule.ts` for why the delay list won over the requirement's "six attempts in total" |
| `next_attempt_at` | **when this becomes due.** The whole schedule is this column |
| `dispatched_at` | set when the relay publishes it; cleared when the next attempt is scheduled |
| `state` | `pending` · `delivered` · `dead` |
| `created_at` | |

**Rules**

- **A delivery is due when `next_attempt_at <= now()` and `state = 'pending'`.**
  There is no timer anywhere. The schedule is a predicate.
- **Nothing waits in the broker.** A delivery enters the stream only when it is
  already due, which is what keeps a dead endpoint from consuming an
  acknowledgement slot for two hours (research R1, measured).
- **Expansion writes every row for one event in one transaction**, together with
  the deduplication claim. An event expanded twice would double every webhook it
  produced, so this is where 3.4's claim mechanism is reused unchanged.
- **The attempt count is the tier.** `attempt = 5` means "the 5-minute tier", not
  "we have tried five times for unclear reasons". Recomputing `next_attempt_at`
  from the tier table is therefore total rather than incremental.
- **Recording an outcome and scheduling the next attempt happen in one
  transaction** — otherwise a delivery can be marked failed with no next attempt,
  which is a webhook that silently stops.

### The relay that drains it

The api gains a second relay beside chapter 3.3's: `SELECT … FOR UPDATE SKIP
LOCKED` over pending rows where `next_attempt_at <= now()`, publish each to the
deliveries stream, mark dispatched (research R13).

The reader has built this loop before. That is the point — the outbox pattern was
never only about events; it is the shape for any work the platform owes itself and
must not lose. The second instance is what makes it a pattern rather than a trick.

---

## `webhook_dead_letters` (new — derived)

| Column | Notes |
|---|---|
| `id` | |
| `environment_id` | **required** — this holds tenant-visible content |
| `endpoint_id` | which endpoint it was bound for |
| `event_id` | the identity a replay reuses, so a replay is still deduplicable |
| `payload` | the body that failed to leave |
| `last_status` / `last_error` | why it stopped, in a form a human can act on |
| `attempts` | how many were made |
| `dead_lettered_at` | when the last attempt failed; retention counts from here |

**Rules**

- **Retained for seven days** (FR-WHK-04), and the chapter must say what happens on
  day eight and mean it. A dead-letter table with no expiry is a place tenant data
  accumulates until an audit finds it.
- **Replayable**, reusing the original `event_id` so a customer who deduplicates
  correctly is not harmed by an operator replaying something they already received.
- **Replay uses current endpoint configuration** — current URL, current secret. An
  endpoint that was fixed is the reason a replay is being asked for.
- **No credential ever lands here.** The payload is the event envelope; the
  signature and the secret are properties of the attempt, not of the event.

---

## The credential model (amended)

Chapter 3.2 established two principals: `application` (an API key, scoped to one
environment) and `user` (an end-user token). The dispatcher is neither.

| Principal | Acts for | Reaches | Accepted on |
|---|---|---|---|
| `application` | one tenant's software | one environment | public + internal |
| `user` | one end user | one environment | public + internal |
| **`platform`** (new) | the platform itself | every environment | **internal routes only** |

**Rule**: the new kind is accepted **only** where a route explicitly opts into it,
and never on a public route. The existing `Accepts` mechanism already expresses
this; what is added is the kind and the credential behind it.

**Why not just give the dispatcher an API key** — the shortcut that would work
immediately and be wrong: an `application` principal is scoped to exactly one
environment by construction. A dispatcher holding one either cannot serve other
tenants, or has been granted cross-tenant reach through the credential type whose
entire meaning is that it has none. Principle I is a correctness property, and this
is the shape its erosion would take.

---

## The `DELIVERIES` stream (new)

The hand-off from the api's relay to the dispatcher. **It carries only work that is
already due** — the waiting happens in `webhook_deliveries`, not here.

| Property | Value |
|---|---|
| subjects | one per delivery, carrying environment and endpoint |
| storage | file |
| retention | limits; bounded age needs to cover a dispatcher outage, not the 2-hour tier |
| ack policy | explicit — the dispatcher acks after reporting the outcome |

**Rule**: nothing sits in this stream waiting for a delay to expire. That is the
whole point of R1's re-plan — a message the broker is holding occupies an
acknowledgement slot, and long delays measured against a real broker were shown to
starve deliveries to healthy endpoints.

**Consequence for retention**: because the stream only ever holds due work, its age
bound is sized for "how long may the dispatcher be down" rather than "how long is
the longest retry tier". Those are very different numbers, and conflating them is
how the first design went wrong.

---

## The delivery request (on the wire)

What a customer's server actually receives. Specified in full in
`contracts/webhooks.md`; summarised here because it is the shape the whole feature
exists to produce.

| Part | Rule |
|---|---|
| method + body | POST, the event envelope chapter 3.3 defined, unchanged |
| event identity | the `id` from that envelope — **the deduplication key**, and documented as such (spec FR-018) |
| timestamp | inside the signed string, so a captured request cannot be replayed indefinitely |
| signature | HMAC-SHA256 over timestamp and raw body, with a scheme version |
| during rotation | one signature per valid secret |

**Rules**

- **Signed over raw bytes.** A recipient who re-serialises the JSON before verifying
  gets a different signature, and the documentation says so in those words — it is
  the single most common way a customer's first integration fails.
- **Everything needed to verify is in the request plus the shared secret.** No
  callback to the platform, no key fetch.
- **The body is the 3.3 envelope, not a new shape.** A webhook that invented its
  own payload would make the event spine's contract a lie at the only hop a
  customer can see.

---

## What the model deliberately does not have

- **No attempt-history table.** Every attempt's timestamp, status, latency and error
  (FR-WHK-06) is the follow-on chapter's, together with the auto-disable rule that
  consumes it — they are one piece of work.
- **No `disabled_reason` column.** It arrives with the rule that sets it. The
  `enabled` flag exists now so that chapter adds a rule rather than a migration.
- **No delivery-state table.** Delivery state lives in the stream, which is what
  makes each delivery independently retryable without the dispatcher holding a
  database it is not allowed to hold.
- **No per-endpoint rate limit or quota.** The limits chapter owns it.
- **No mail.** FR-WHK-07's notification needs email infrastructure the workspace
  does not have, and FR-RTL-07 will need the same — it wants a home of its own
  rather than arriving as a side effect of a webhook chapter.
