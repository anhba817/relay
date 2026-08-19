# Research — chapter 3.8, "Limits you can see coming"

Phase 0. Ten items. R3 is the chapter's central decision and the spec deliberately
left it open. R5 found a **second unenforced contract** the chapter has to close
whether it wants to or not. R10 quantifies the size risk the spec flagged and the
answer is not the one the scope decision assumed.

---

## R1 — The bucket algorithm, and what the SAD already decided

**The question.** SAD §6.3 lists `rl:{env}:{bucket}` → "Token buckets (FR-RTL-01)"
with TTL "window". Token bucket, fixed window and sliding window are three
different algorithms with three different header semantics. Which is specified?

**What the SAD actually pins**: the key shape, the store, and the TTL. It names
"token buckets" but the TTL column says "window", which is a fixed-window
property — a true token bucket refills continuously and has no window to expire.
The two halves of that row describe different algorithms.

**Decision: fixed window, and say so.** Three reasons, in order of weight.

`X-RateLimit-Reset` is the deciding one. The header has to name a moment when the
allowance returns, and a fixed window has exactly one such moment. A continuously
refilling bucket does not — the honest answer for "when will I have my full
allowance back" is a curve, and the header is an integer. A limiter whose reset
header is a lie fails FR-002 in the way that matters, because FR-002 exists so a
client can schedule against it.

Second, atomicity. `INCR` returns the new value and is atomic on its own;
`EXPIRE` on first increment gives the window. Two commands, no Lua, no
read-modify-write race between api instances. A token bucket needs
read-timestamp-compute-write, which across instances needs a Lua script — more
machinery to teach for a header the algorithm then cannot fill in honestly.

Third, the TTL does the cleanup. A fixed-window key expires when its window ends,
so nothing accumulates and no sweep is needed. This matters more than it sounds:
this chapter has watched four test suites break because a shared store grew
without bound (chapter 3.7's baseline, T021a).

**The cost, stated rather than hidden.** Fixed windows allow a burst of up to
twice the limit across a boundary — the last instant of one window plus the first
instant of the next. That is the textbook objection and it is real. It is accepted
here because the limit's job is to bound sustained load, not to smooth
instantaneous rate, and because the alternative buys smoothing with a header that
cannot be computed. The chapter states the burst rather than pretending the
algorithm is stricter than it is.

**Alternatives considered.** Sliding window log (a sorted set per bucket, one
member per request) — rejected: it stores one entry per request in a store the SAD
says holds ephemeral state only, and it makes memory proportional to traffic.
GCRA / leaky bucket via Lua — rejected for the `Reset` reason above, and because a
Lua script is a second language in the request path (constitution VII).

---

## R2 — Where the limiter attaches, and why there are two positions

**The question.** One mechanism, but the tenant limiter needs to know which
environment is calling and the auth limiter has to work when the caller is nobody.
Where do they go in a chain that is currently `RequestContextMiddleware →
AuthenticateMiddleware → CredentialGuard → handler`?

**Two positions, and the ordering is forced.**

The tenant limiter goes **after** `AuthenticateMiddleware`. It counts per
environment (FR-006) and the environment comes from the credential, which the
middleware resolves. Nothing earlier in the chain knows the tenant.

The auth limiter goes **at** `AuthenticateMiddleware`, counting failures by source
IP (FR-012). It cannot go later: a request that fails authentication never reaches
a middleware placed after it. It cannot key on tenant: the whole point is that the
caller has not proved which tenant they are.

**Middleware rather than a guard, and this is the second time.** Chapter 3.2 put
authentication in middleware rather than a guard, with a comment recording the
reason: Nest constructs request-scoped providers before the enhancer chain runs, a
finding chapter 2.6 paid for. The same constraint applies here, plus one of its
own — FR-002 requires the three headers on **successful** responses, and a guard
that returns `true` has no natural place to set a header on the response that has
not been generated yet. Middleware has `res` in hand before the handler runs.

**Decision.** A `RateLimitMiddleware` applied after `AuthenticateMiddleware` for
tenant limits; the auth-failure count lives inside the authentication path where
the failure is already known. Two call sites, one bucket implementation.

**What this makes easy to get wrong**, and therefore what needs a test: the
internal service seam. Dispatcher-to-api and gateway-to-api calls carry a service
credential and would otherwise be throttled as customer traffic (FR-009). The
middleware has to exempt them, and the exemption has to be tested, because a
limiter that throttles the dispatcher turns a busy customer's webhooks into a
platform-wide stall.

---

## R3 — The two failure directions, and how the auth limiter avoids both wrong answers

**The question the spec left open.** FR-010 requires the tenant limiter to fail
open when Redis is unreachable. FR-011 requires the auth limiter not to allow
unlimited attempts in the same outage. Failing closed on authentication makes a
Redis restart a login outage, which is its own incident. What is the third answer?

**Decision: an in-process fallback counter, per instance, with the same
threshold.**

When the shared store is unreachable, the auth limiter counts in a bounded
in-memory map keyed by source IP, with the same threshold and window. The
guarantee weakens from "N attempts per window across the fleet" to "N per window
per instance" — so an attacker who can reach every instance gets N × instances.

**Why that is the right weakening.** The three candidates and what each costs:

| Behaviour during a Redis outage | Attacker gets | Legitimate users get |
|---|---|---|
| Fail open | unlimited attempts | service |
| Fail closed | nothing | no logins at all |
| **In-process fallback** | **N × instance count** | **service** |

Fail open is unbounded and therefore not a degradation but a hole. Fail closed
converts a cache outage into an authentication outage, which is worse than the
attack it prevents for every customer who is not being attacked. The fallback is
bounded, and the bound is a small multiple rather than infinity — a platform
running three api instances gives an attacker three times the attempts for the
duration of the outage, not three thousand.

**Why the tenant limiter does not get the same treatment.** It could, and it must
not, because the two limiters are protecting different things. The tenant limiter
protects Relay's capacity from a customer's traffic; over-serving a paying customer
for the length of a Redis outage costs some capacity. The auth limiter protects a
customer's credentials from an attacker; over-serving an attacker costs the
customer their account. Same code, and the asymmetry is in what is on the other
side of the limit.

**The memory bound is part of the decision, not a detail.** An in-memory map keyed
by attacker-controlled source IP is a memory-exhaustion vector if it is unbounded —
the fallback would then be a worse hole than the one it closes. It is capped, and
on reaching the cap it stops admitting new keys rather than evicting old ones,
because evicting is what an attacker would drive.

**Alternatives considered.** A stricter threshold in fallback mode (say N/4) —
rejected as a number with no derivation; the same threshold per instance is at
least explicable. Failing closed on authentication only for credentials that have
already failed once — rejected: it needs the state whose absence is the problem.

**This decision has no code of its own to point at**, which is why SC-007 requires
a sabotage mutation that makes the auth limiter fail open. Chapter 3.7 learned this
the hard way: its central decision (never retire the mark) had no test behind it
until a mutation said so.

---

## R4 — Default limits: chosen, and the derivation written down

**The question.** The SRS specifies no numbers for FR-RTL-01. Any value is a
business decision dressed as a technical one.

**Decision.** Per environment, per minute:

| Operation | Limit | Where the number comes from |
|---|---|---|
| REST requests | 600/min | 10/s sustained. NFR-PRF-02 puts REST write p95 under 150 ms, so 10/s is well inside one instance's comfortable throughput and generous for the integration this platform is sold for |
| Message sends | 600/min | The same number, because a send IS a REST request on the public path; two different numbers would mean a client hitting one limit while the other says it has room |
| Connection establishment | 60/min | FR-RTM-09 allows a user five concurrent connections. Sixty establishments a minute per environment is a client reconnecting hard, not a client working |
| Failed authentication | 10/min per IP | Low on purpose. Ten wrong credentials a minute from one address is not a human mistyping |

**Configurable, with these as defaults** (FR-007). The right number is a plan
question for a real deployment and this platform has no plans yet.

**Where the policy lives: Postgres, on the environment.** Not Redis — the policy
is not ephemeral and losing it must not silently grant unlimited traffic. Not a
config file — FR-RTL-04's independence is per environment and a file is per
deployment. A nullable column on `environments` meaning "use the default" keeps
the migration to one statement and makes "unconfigured" a state the code has to
handle rather than a value someone has to seed.

**The burst consequence of R1, in numbers**: a 600/min fixed window allows up to
1,200 requests across one window boundary. Stated in the chapter.

---

## R5 — A second contract declared and never enforced: `request_id`

**Found while checking FR-003.** The spec requires the `429` body to carry `code`,
`message`, `docs_url` and `request_id`, which is constitution V's four-field error
envelope. The platform sends three.

`packages/protocol/src/frames.ts`, the error frame's own comment:

```text
/** Protocol-level error — EIR-API-04's error shape, reused on the socket
 * (this chapter's recorded decision). `request_id` joins in Part 2, when a
 * gateway exists to mint one. */
```

Part 2 came and went. A gateway exists, it mints request ids, and the field was
never added. `ProtocolErrorFilter` builds `{ code, message, docs_url }`;
`service-kit`'s 404 shape does the same. The id is on the response as
`X-Request-Id` and absent from the body a client parses.

**This is the chapter's own subject, twice over.** `rate_limited` and close code
4008 have been declared and unenforced since chapter 1.3. So has the fourth field
of the error envelope. Three pieces of the same vocabulary, all written down, none
wired up — and the reason is the same in all three cases: a contract is cheap to
declare in the chapter that invents it and only becomes work in the chapter that
has to honour it.

**Decision: add `request_id` to the error envelope everywhere, not only on the
429.** A four-field envelope on one status and a three-field envelope on the other
five is worse than either consistent answer, and constitution V does not say "on
rate-limit errors". This touches `frames.ts`, `ProtocolErrorFilter` and
`service-kit`, and all three are fenced in earlier chapters — the amendments are
this chapter's to carry because this chapter is where the envelope is discussed.

**What it costs**: the schema goes from `strictObject` without the field to one
with it, so every existing construction site must supply it. That is the whole
point of `strictObject` and the compiler will find them.

---

## R6 — What a degraded response says

**The question.** FR-014 requires a client be able to tell "you have N left" from
"we are not counting right now".

**Decision: omit `X-RateLimit-Remaining` and `X-RateLimit-Reset`, keep
`X-RateLimit-Limit`.**

The limit is still true — it is policy, read from Postgres, and the outage is in
the counter. The remaining count and the reset time are the two values that only
exist because something was counting, and inventing them is the failure FR-014
forbids. A client that reads `Limit` with no `Remaining` learns exactly what
happened: the policy stands, the accounting is unavailable.

**Rejected: a sentinel.** `X-RateLimit-Remaining: -1` or `: unknown` requires
every client to know the sentinel, and a client that does not will parse `-1` as a
number and conclude it is over its limit. An absent header is unambiguous to code
that checks for presence and harmless to code that does not.

**Rejected: dropping all three.** `Limit` is not degraded and removing it throws
away information the platform still has.

**Also required by FR-013**: one log line per degradation, naming it, carrying no
credential. Rate-limited at the logger rather than per request — a Redis outage
under load would otherwise produce one line per request, which is how an outage
becomes two outages.

---

## R7 — Refusing a WebSocket: 429 before the handshake, and why 4008 stays unused

**The question.** The gateway's upgrade handler deliberately completes the
handshake before refusing, so it can send close code 4001 — its comment says
EIR-WS-05 wants the close code "on a connection we never really opened". Does a
rate-limited handshake follow that pattern?

**Decision: no. Refuse with an HTTP `429` during the upgrade, before the
handshake.**

FR-005 requires the refusal to happen before the socket is accepted, and the
reason is the header: `Retry-After` is an HTTP header and there is nowhere to put
it on a close frame. A client refused with `429 Retry-After: 30` knows what to do.
A client closed with a code has to look the code up and then guess the interval.

The inconsistency with 4001 is deliberate and worth the chapter explaining: an
invalid token is a permanent condition the client must be told about precisely, and
a close code carries that. A rate limit is a temporary condition with a duration,
and HTTP already has the vocabulary.

**Close code 4008 stays unused.** It reads "quota exhausted", and a rate limit is
not a quota — that is the distinction this whole chapter is built on. 4008 belongs
to chapter 3.9, where a quota can actually be exhausted. So this chapter enforces
one of chapter 1.3's two unused constants and explains why the other still waits,
which is a better outcome than using it because it was there.

**Frames on an open connection** take `rate_limited` in an `error` frame and the
connection stays open (FR-004). Closing a socket because one frame was too fast
would make the client reconnect, which costs a handshake and consumes the
establishment limit — a limiter that punishes the limited into hitting a second
limit.

---

## R8 — The notification transport is the outbox pattern, a third time

**The question.** FR-016 through FR-024 need a mail path with retry, no
double-send, no lost obligation, and no effect on anything else when it breaks.
That sounds like new machinery.

**It is machinery this platform has built twice.** `webhook_disable_notifications`
already has the shape: a row per obligation and a `delivered_at` that is null until
the obligation is met. That is an outbox table with the column named differently.

Chapter 3.3 built the pattern — `SELECT … FOR UPDATE SKIP LOCKED`, act, mark.
Chapter 3.5 built the second instance for webhook deliveries and the chapter's
argument was that a second instance is what makes it a pattern rather than a trick.
This is the third, and it needs no new column, no migration, and no new abstraction:
claim undelivered notifications, send, set `delivered_at`.

**The properties fall out of the shape rather than needing to be built.**

- FR-018, a failed send is retried and the obligation is not lost: the row is not
  marked, so the next pass claims it again.
- FR-019, not sent twice: `delivered_at IS NULL` in the claim predicate.
- FR-017, marked only after acceptance: the mark is after the send returns, in the
  `finally` for the reason chapter 3.3 recorded — whatever went wrong with row N+1,
  rows 1..N really did go out.
- FR-020, the rows accumulated since 3.6: they are undelivered work by the
  predicate's own definition. Nothing special happens; they are simply claimed.

**FR-024, failing alone.** The loop is a background relay, not a request path, so a
dead mail server cannot fail a customer's request. This is constitution III's
argument — analytical failures must not touch the operational path — applied to a
third path, and the wording is worth being careful about: it is not that
notification is *less* important, it is that it must not be *coupled*.

**One thing the shape does not give for free.** An endpoint disabled, re-enabled
and disabled again writes two rows and must send two emails (edge case), which the
predicate handles, but an endpoint that flaps repeatedly would send an email per
flap. Out of scope to solve — 3.6's hour-long failure run already makes flapping
expensive — but named in the chapter so it is a known shape rather than a
surprise.

---

## R9 — Mail in development: a container, and the recipient problem

**Decision: Mailpit in `compose.yaml`, and `nodemailer` for SMTP.**

Mailpit because it is one container, needs no account, holds messages in memory,
and exposes both SMTP and an HTTP API — so a test can assert on what was
*received* rather than on what the sender believed it sent. That distinction is
the whole reason to run a mail service rather than stub the transport: FR-021 says
no email may contain a signing secret, and the only way to check the contents of
an email is to read the email.

MailHog is the better-known choice and is unmaintained; that is the only reason it
is not this.

`nodemailer` because SMTP by hand is not this chapter's subject. It is the first
new runtime dependency since chapter 3.4's `nats` client.

**Against constitution VII.** "Boring by design" asks new infrastructure to justify
itself. The justification: FR-025 requires local development to receive and inspect
these emails with no external account and no outbound internet, and the
alternatives are a stubbed transport nobody can verify or a real SMTP credential in
a tutorial repository. A container that exists only in `compose.yaml` and never in
a deployment is the smaller commitment. It is also the fourth store in a file that
already has four, and it is worth the chapter noting that this is the first time
since 3.4 that the answer to "do we need another moving part" was yes.

**The recipient problem, which is not a detail.** `humans.email` is **nullable**.
`memberships.role` is one of `owner`, `admin`, `member`. So "email the
organisation's admins" resolves to owners and admins of the organisation the
notification row names — and some of them may have no address. FR-023 requires
that a notification which cannot be addressed is not marked delivered and the
condition is visible, which means the unaddressable case is a real branch with a
real test, not a defensive `if`.

Recipients are resolved **at send time** from `organisation_id` on the row
(FR-022). Chapter 3.6 denormalised that column for exactly this reason and wrote
the reason down: an application moving between organisations must not silently
retarget a notification already owed to somebody else. This chapter is the first
code to depend on that decision, which is a good test of whether it was worth
making.

---

## R10 — The size risk, measured, and the recommendation the numbering did not expect

**The spec flagged this and the plan is where it gets a number.**

Fence estimate by area, counting files this chapter must show:

| Area | Files |
|---|---|
| Bucket logic and its unit tests | 2 |
| Redis-backed store | 1 |
| Rate-limit middleware + tests | 2 |
| Auth-failure limiter + in-process fallback + tests | 2 |
| Wiring: `app.module.ts`, `authenticate.middleware.ts` | 2 |
| Limit policy: migration, `schema.ts`, `repository.ts` | 3 |
| Gateway: handshake refusal, frame limiting, tests | 2 |
| Error envelope: `frames.ts`, `protocol-error.filter.ts`, `service-kit` | 3 |
| Integration suite for limits | 1 |
| `package.json` (ioredis), `compose.yaml`, coverage config | 3 |
| **Rate limiting subtotal** | **23** |
| Mailer + tests | 2 |
| Notification relay + tests | 2 |
| `repository.ts` claim (already counted above) | 0 |
| Notifications module, wiring | 2 |
| Integration suite for notifications | 1 |
| `package.json` (nodemailer) | 0 (counted) |
| **Transport subtotal** | **7** |
| **Total** | **~30** |

**For comparison, measured rather than remembered**: chapter 3.5 shipped 39 fences
against a budget first estimated at 22 and ran 4,952 prose words; chapter 3.6
shipped 21 and ran 5,273. The bound is 2,000–4,000.

**Finding: 30 fences will not fit inside the word bound, and the transport is the
separable seven.** The rate-limiting 23 is one mechanism with one argument — the
failure directions — and it is already at 3.6's fence count. The transport's seven
carry a different argument (the outbox, a third time) and a different failure mode.

**Recommendation, recorded rather than acted on:** the transport should be its own
chapter, sitting between this one and quotas. It is the third instance of a pattern
the series has taught twice, which is a chapter with a point rather than a section
with a chore, and it is what FR-RTL-07's threshold email will need anyway.

**This is not the plan's decision to make.** The scope was chosen deliberately, with
the cost of adding the transport stated at the time — what was not available then
is this number. The plan proceeds with both halves and shapes the tasks so the
transport is the **last** phase and separable: if the word count runs past the
bound, the transport lifts out into its own chapter without unpicking the limiter.
Phase order is doing the hedging so nobody has to decide twice.

**If both halves ship together**, the chapter will be over the bound and the
battery must say so with the number, as 3.6's did.

---

## The renumbering, which cost nothing

Recorded because the prediction was tested rather than trusted.

Chapter 3.7 rewrote three source comments to name subjects instead of chapter
numbers, on the argument that a forward reference in a fenced file goes stale on
every insertion and costs a fence amendment to fix. Its success criterion drove
forward references in live source to zero.

This renumbering moved two chapters. The cost:

  `docs/07-tutorial-plan.md`         table row and narrative
  `relay-tutorial/lib/tutorial.ts`   three entries
  published prose, both locales      4 references
  fenced source files                **0**
  fence amendments                   **0**

3.7's own renumbering needed two post-series amendments and a section of prose to
explain why a comment was already stale. One chapter later the same operation is
prose-only. The rule paid for itself in one chapter, which is faster than most
rules of its kind.

---

## What this chapter does NOT do

- Quotas, spending caps, threshold emails, quota degradation — chapter 3.9, and the
  metering they need arrives in Part 4.
- FR-RTM-09's concurrent-connection cap. It needs the `conn:{env}:{user}` registry
  the SAD specifies and the gateway does not have; presence needs the same
  registry and they belong together.
- A dashboard view of remaining allowance. There is no dashboard; the headers are
  the API-side half of constitution V's promise.
- Per-API-key limits. The SRS says per-tenant and the environment is the boundary
  constitution I enforces.
- Using close code 4008. It means quota exhausted and no quota exists yet.
