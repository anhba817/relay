# Research — chapter 3.8, "Limits you can see coming"

Phase 0. Twenty-seven items. R3 is the chapter's central decision and the spec
deliberately left it open. R5 found a **second unenforced contract** the chapter
has to close whether it wants to or not. R10 quantifies the size risk the spec
flagged and the answer is not the one the scope decision assumed. **R11 was added
after the first `/speckit-analyze` pass** (nothing said which bucket a REST send
decrements) **R12, R13 and R14 after the second**, which found two
architectural gaps — the gateway cannot read the policy, and it has no request id to
put in the field R5 requires — **R15 after the third**, which found that the auth
limiter would refuse this project's own test suite, and **R16 after the fourth**,
which corrected a rule the third pass had written from memory.

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

**Does contradicting the SAD need an ADR?** Chapter 3.2's research answered the
same question about ADR-05 and the answer here is the same in form: no. This is a
service-local algorithm choice inside a component the SAD already places, not a new
architectural boundary — the store, the key prefix and the ephemerality are all
unchanged, and constitution VII asks for an ADR when a *decision* changes, not when
an implementation reads a document's own inconsistency in the direction its TTL
column points. If a reviewer wants it recorded architecturally, the right form is a
sentence in SAD §6.3 replacing "Token buckets" with "Fixed-window counters",
because that row currently names two algorithms at once.

**Reversal condition** — the thing R1 was missing and constitution VII asks for:
revisit if a customer needs the boundary burst smoothed, or if `X-RateLimit-Reset`
stops being a required header. Either removes the reason fixed window won.

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

**Ports are off-default** — `18025` for HTTP and `11025` for SMTP — matching the
`15432`/`16379`/`14222` convention every other store in `compose.yaml` follows, so
the lane cannot collide with a container a developer is already running.

**A fifth container has to be registered, not just declared.** `@relay/config`
exports `INFRA_SERVICES` above a comment saying it *names* the local infrastructure
so the workspace need not parse YAML, and `infra.test.ts` pins it to `compose.yaml`.
Mailpit joins the list, gets a healthcheck in the shape the other four use, and adds
no entry to `DURABLE_VOLUMES` — it holds messages in memory, which is the same
reasoning the Redis entry already records.

**The healthcheck is not decoration.** `infra.test.ts`'s comment states the cost:
*"if a healthcheck disappears … `docker compose up -d --wait` would silently stop
meaning ready."* Without one, `--wait` waits for *running* and the quickstart's V9
can read Mailpit's API before it serves.

**The gate could not have caught either.** `infra.test.ts` asserts that compose
declares every `INFRA_SERVICES` entry — one direction. A container in compose and
missing from the list is invisible to it, which is exactly how this went unnoticed
until the fifth analysis pass. The reverse assertion is added with the service.

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
| **Subtotal as first estimated** | **23** |
| *Added by remediation:* `internal.ts` (limits and client address on the internal contract) | 1 |
| *Added by remediation:* `services/gateway/src/limits.ts` + its unit test (R12: the gateway needs its own helper) | 2 |
| *Added by remediation:* `registry.ts` (the limits on `Connection`) | 1 |
| *Added by remediation:* the api's session controller (answering with the limits) | 1 |
| *Added by remediation:* `turbo.json` and `packages/e2e/src/harness.ts` (R19: strict env mode, two allowlists) | 2 |
| *Added by remediation:* `eslint.config.mjs` (R20: confining the second driver) | 1 |
| *Added by remediation:* `packages/config/src/infra.ts` + `infra.test.ts` (R9: registering a fifth container) | 2 |
| **Rate limiting subtotal** | **33** |
| Mailer + tests | 2 |
| Notification relay + tests | 2 |
| `repository.ts` claim (already counted above) | 0 |
| Notifications module, wiring | 2 |
| Integration suite for notifications | 1 |
| `package.json` (nodemailer) | 0 (counted) |
| **Transport subtotal** | **7** |
| **Total** | **~40** |

**For comparison, measured rather than remembered**: chapter 3.5 shipped 39 fences
against a budget first estimated at 22 and ran 4,952 prose words; chapter 3.6
shipped 21 and ran 5,273. The bound is 2,000–4,000.

**Finding: the fences will not fit inside the word bound, and the transport is the
separable seven.** The rate-limiting half is one mechanism with one argument — the
failure directions.

**The estimate moved three times, always upward.** 23 and 30 when first written; 28
and 35 after the passes that found the gateway is not the api; **33 and 40** after the
passes that found the platform's quiet enforcers — two env allowlists, a lint rule, and
an infrastructure inventory. Every addition was a file some earlier chapter had already
fenced.

**33 for one half is half again as much as chapter 3.6's entire 21.**

**And the number itself is the wrong kind of artifact.** It has gone stale in three
separate analysis passes, each time because a remediation added a task below the
sentence stating how many there were. T058's gate therefore **derives** the count from
the published page rather than comparing against this table: a written total describing
something the page also enumerates is a second source of truth, which is the fault this
feature has now diagnosed in five other places. The transport's seven
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

## R11 — Which bucket a send decrements

**Raised by the first analysis pass, and rewritten after the sixth found its first
answer was built on a capability the platform does not have.** Both versions are kept
below, because the mistake is more instructive than the fix.

**The question.** Three buckets are defined — `rest`, `send`, `connect`. A
`POST /v1/channels/{id}/messages` is both a REST request and a message send. Which
does it decrement, and FR-002 describes one set of headers, so which does it report?

### What the first answer said, and why it was wrong

It said both are decremented, headers report whichever has fewer remaining, and
justified the two buckets as answering "different questions: how much traffic, and
how many messages" — with the worked example that *"a batch of ten messages in one
request decrements `rest` by 1 and `send` by 10"*.

**There is no batch send.** `sendMessageBodySchema` is a `strictObject` with a single
`text` field, and `messageSendSchema` on the socket is the same: one operation, one
message, both transports. That request cannot be made.

So on the REST path both counters moved by exactly one, both defaults were 600, and
they would have exhausted in the same instant. The `send` bucket contributed nothing,
the header rule chose between two identical numbers, and FR-008's "distinguishing
test" was unwritable.

**Read the schema, not the plan.** The rationale was reasoned out of the
documents — every one of which was written by the same process that had never opened
`messages.schema.ts`.

### The answer that survives contact with the code

**`send` counts messages wherever they enter. `rest` counts HTTP requests.**

| Operation | `rest` | `send` |
|---|---|---|
| `POST …/messages` | +1 | +1 |
| a `message.send` frame on an open socket | — | +1 |
| any other REST call | +1 | — |

**What this keeps from the first answer.** Its one real insight: a limit a client can
lift by moving the same traffic to the socket is not a limit. A message costs the same
downstream whichever door it came through, so one budget covers both doors.

**What it drops.** The fiction that a request can carry many messages.

**The two counters now genuinely differ**, so "the headers report whichever has fewer
remaining" is a rule with work to do rather than a tie-break between equal numbers. A
client sending over both transports spends `send` twice as fast as `rest`.

**And the distinguishing test exists.** Five sends over REST and five frames over the
socket leave `send` at 10 and `rest` at 5. That is what FR-008 asks for, and it is
buildable.

### Which service counts what, and why the counter is in Redis

The gateway does not send through the public REST route; it calls
`api.sendMessage(...)` over the internal seam, which FR-009 exempts from customer
limits. So a socket send is counted **by the gateway**, against the same
`rl:{env}:send:{window}` key the api uses for REST sends.

**That shared key is why the counter lives in Redis rather than in either process.**
Two services increment one bucket, and neither can see the other's memory. The
exemption stays coherent: the gateway's internal call is not counted a second time as
REST traffic, because the gateway already counted the send.

**The refusal names which limit was reached** in its `message` — "too many requests"
and "too many messages" are different problems, and on the socket only the second can
happen. The `code` stays `rate_limited`; neither message names a credential
(NFR-SEC-06).

**Alternatives considered.** `send` covering the socket only and `rest` covering
HTTP — rejected for the transport-hopping reason above, which is the part of the
first answer that was right. One bucket for everything — rejected: it cannot express
"a client hammering history reads" and "a client flooding messages" as different
loads, which is the distinction the two numbers exist for.

## R12 — How the gateway learns a limit it cannot read

**Raised by the second analysis pass.** The policy is three columns on
`environments` in Postgres. The gateway has no Postgres — `registry.ts` says so as
a design statement: *"Note what else is absent: no pg, no drizzle-orm, no
repository import."* Its dependencies are `@relay/protocol`,
`@relay/service-kit`, `ioredis`, `jose` and `ws`. So it cannot read
`connect_limit_per_minute` or `send_limit_per_minute`, and FR-007 carves out no
exception for the socket.

**Decision: the api's session response carries them, and the gateway caches them on
the `Connection`.**

The gateway already makes exactly one api call at the upgrade —
`authenticate(api, token)` — and it already returns more than a yes: identity *and*
memberships. Adding the environment's two limits is one more field on a round trip
that is happening anyway. No new call, no new dependency, and the api stays the only
service that reads Postgres.

**This is the same move chapter 3.2 made on the same call.** Its comment records it:
*"the api verifies, and answers with the identity AND the memberships. This is the
same one call the connect path already made — it just asks a better question than
'what may this user hear'."* Asking it for the limits as well is that sentence a
second time.

**Where the limit lives once the socket is open.** On the `Connection`, beside the
`marks` chapter 3.7 put there, and for the same reason: it describes one socket and
dies with it. The alternative is a policy read per frame, which puts Postgres on the
hot path of the thing the limit exists to protect.

**The consequence, stated rather than discovered.** A limit changed while a socket
is open does not apply to that socket until it reconnects. A long-lived connection
can outlive a policy change by hours. That is the cost of not reading Postgres per
frame and it is the right trade — but it is a real property and the chapter says it
rather than letting a reader assume otherwise.

**Rejected: giving the gateway a database client.** It would make the limit
configurable on the socket immediately and it would spend an architectural property
three chapters have protected to buy it. Constitution VII asks new dependencies to
justify themselves against the "deliberately not a separate service" reasoning, and
"so a rate limit can be reconfigured without a reconnect" does not clear that bar.

**Rejected: defaults only on the socket, narrowing FR-007.** Defensible, and it
makes the requirement smaller rather than the design better. It also produces the
worst outcome if nobody notices — a spec claiming per-environment configurability
while one of the three limits quietly ignores it.

---

## R13 — Does a socket error frame have a `request_id`?

**R5 asserted that a gateway exists and mints request ids. It does not.** There is
no `newRequestId`, no `requestId` and no `request_id` anywhere in the gateway. Its
`sendError` builds `{ code, message, docs_url }` and has nothing to add. Making the
field required on `errorFrameSchema` — a `strictObject` — breaks every call site
with no value available.

**Decision: the field is required, and the gateway mints one.**

Per inbound frame it answers, for a frame that was answering something; the
connection's own id for a frame nobody asked for. `@relay/service-kit` already
exports `newRequestId` and the gateway already imports that package, so this is an
import and a field.

**Why not make it optional on the frame.** That is the tempting answer — a
server-initiated frame is not a response to a request, so constitution V's "every
error response carries the request_id" arguably does not reach it. It is rejected
because **an optional field is the exact pattern this chapter exists to talk
about.** `rate_limited` was declared and never emitted. Close code 4008 was declared
and never sent. `request_id` was promised for Part 2 and never added. Closing the
third by declaring it optional would be the fourth instance of the same habit, in
the chapter that names the habit.

**What the id is for, which decides the shape.** A developer quoting an id in a
support ticket needs it to find one server-side log line. On REST that is one
request. On a socket, the useful unit is the frame that failed — a client whose
tenth `message.send` was refused needs to point at that refusal, not at the
connection. So: an id per answered frame, and the connection's id when there was no
frame to answer.

**The asymmetry this leaves**, named because it will look like an oversight: the
REST envelope's `request_id` also appears in the `X-Request-Id` header, and the
socket's does not, because a frame has no headers. The id is in the payload in both
cases; only the duplicate is missing.

---

## R14 — The handshake limit runs after an api round trip, and the api counts the wrong IP

**Two findings, one cause.** The gateway's upgrade handler authenticates before it
can key a bucket, because the environment comes from the token. So the connect limit
caps *sockets*, not *authenticate calls* — a flood of garbage tokens gets one api
call each, at whatever rate the attacker can open TCP connections.

FR-AUT-12 is supposed to cover that: failed authentication limited per source IP.
**It does not, and the reason is worse than the ordering.** The api counts against
the IP it sees, and for a socket handshake that is *the gateway's* IP. Every client
in the fleet shares one counter, so ten failed handshakes from ten customers look
like ten failures from one address — and a single attacker exhausts a threshold that
then refuses everybody.

**Decision: the gateway forwards the client's address on the internal
authentication call, and the api counts against that.**

The internal seam is exempt from *customer rate limits* (FR-009) and must not be
exempt from *counting the end client's failures* — those are two different things
that a single "is this the internal seam" check would conflate. The exemption
answers "should this call be throttled as traffic"; the counting answers "whose
failure was this". A gateway-originated call is exempt from the first and must
supply an answer to the second.

**The interesting part survives the correction**, and it is worth a section in the
chapter: the api must believe the gateway about *who failed* while believing nothing
about the credential that failed. The address is forwarded on the internal contract
rather than read from a header a caller could set, because chapter 3.2 removed exactly
that pattern — a header the caller asserts is a header the caller can forge.

**What this does not fix.** The api still does an authentication lookup per bad
handshake; the limiter now refuses after the threshold instead of never. Shedding
before the lookup would need a per-IP check inside the gateway with its own store
and its own fallback, and that is a second limiter with a second failure direction
in a chapter already carrying two. Named as a known gap rather than built, and it
belongs with the connection registry work FR-RTM-09 needs.

---

---

## R15 — The auth limiter will refuse this project's own test suite

**Raised by the third analysis pass**, and it is the third appearance of one shape:
a shared resource newly constrained, and suites that had been passing on headroom.

**The numbers.** The threshold is 10 failed authentications per minute per source
address. The api integration lane asserts `401` or `403` **26 times**, eight of them
in `credentials.itest.ts`, and it runs in about 110 seconds. Every one of them comes
from `127.0.0.1`, so they all share one bucket.

Only 401s count — a `403 wrong_credential_type` is a valid credential of the wrong
class, which is a successful authentication — so the true figure is lower than 26.
It is not lower than 10 with any margin worth relying on.

**The failure mode is worse than the failure.** FR-028 requires the rate-limit
refusal to be indistinguishable from a wrong-credential refusal, so that the limiter
cannot be used as an oracle. That is right, and it means a test expecting
`code: "unauthorized"` receives `code: "rate_limited"` at the same status — and a
test that authenticates *successfully* after its neighbours have failed enough times
sees a refusal with no local cause. Chapter 3.7 spent four attempts and about four
hours on that class of confusion.

**Decision: the threshold is configuration with a default of 10, read from
`RELAY_AUTH_FAILURES_PER_MINUTE`.**

The data model already calls the auth threshold "configuration, not policy" — it is
not per environment, because the caller has not proved which environment they are.
This makes that sentence operational. Suites that deliberately submit bad
credentials raise it; the limiter's own suite sets it *low* on purpose, which is the
only way to test a threshold at all.

**The default enforces, and that is not incidental.** Chapter 3.6 added
`RELAY_DISABLE_SWEEP` with a comment worth repeating: *"DEFAULT ON. A flag whose
default disabled a requirement would be a requirement nobody had built."* The same
rule applies here in the other direction — the default is the enforcing value, and a
test that wants headroom asks for it explicitly and visibly.

**Measure before choosing, not after.** The first task counts the actual failed
authentications per minute in the lane rather than reasoning from 26 assertions.
Chapter 3.7's baseline found that a count of assertions is not a count of requests,
and its own sweep fault turned on exactly that difference — an assertion that
`disabled >= 1` passed while the endpoint under test was never reached.

**Rejected: raising the default so the suite fits.** That is choosing a security
threshold to suit a test, which is how a limit becomes decorative. Ten wrong
credentials a minute from one address is not a human mistyping, and the number
should survive the suite rather than the reverse.

**Rejected: leaving it and fixing whatever breaks at T035.** It would work and it
would produce the least useful form of the information — "some tests fail" at the
end of the chapter, in a lane this project has spent two chapters getting green.

---

---

## R16 — Where a chapter's fence diff starts, verified rather than remembered

**This item exists because the third analysis pass wrote the rule down wrong**, and
the fourth caught it. Recording the method as well as the answer, since the method
is what failed.

**The answer, read out of `scripts/check-fence-chain.mjs`.** `replay()` walks every
chapter page in `part.chapter` order and applies each fence to the accumulated state
for that file. Only after every chapter has been replayed does the script read
`fences/post-series.md` and apply those diffs. The result is then compared to the
file on disk.

So the state a chapter-3.8 fence amends is **all chapters through 3.7** — which, for
any file post-series does not touch, is exactly HEAD. `pnpm check:fences` passing at
`part3-ch7` is the proof of that, not an assumption about it. `git diff
part3-ch7..HEAD -- <file>` is the correct base.

**The one exception, and it cuts both ways.** For a file post-series already amends,
the chapter chain stops short of HEAD by that amendment. A `part3-ch7` base would
carry a pre-image the chain rejects — and a new chapter fence would also land
*underneath* the existing post-series diff, whose own pre-image would then no longer
match. One change, two failures.

Five files are amended today: the **root** `package.json`, `credentials.itest.ts`,
`consumer.itest.ts`, `signup.itest.ts` and `deliveries.itest.ts`.

**What the third pass got wrong, and why.** It generalised from chapter 3.7's
`consumer.itest.ts` failure — a post-series diff regenerated from `part3-ch6..HEAD`
when that file's chain ends in chapter 3.4 — into "an amendment diff's base is the
chain's end state, not the latest tag". True of post-series diffs; false of chapter
fences, where the tag *is* the chain's end state. The instruction would have sent an
implementer looking for a Part 1 base for `frames.ts` that they did not need.

It was written from memory of a debugging session rather than from the script. The
correction was written by reading `replay()`.

**And the fourth pass's own first instance was wrong too.** It reported `package.json`
as a live collision because chapter 3.8 adds `ioredis` and `nodemailer` to
`services/api/package.json`. The post-series entry is for the **root** `package.json`
— turbo's `coverage` script — and the two are different files with the same basename.
The real collision is `credentials.itest.ts`, which T025d has to touch to raise the
auth threshold.

**The rule that comes out of all three mistakes**: check the post-series title list
before generating a fence, and match on the full path rather than the basename.

---

---

## R17 — Which routes the limiter applies to: limit once, at the door it entered

**The seventh pass produced three findings that are one decision.** FR-009 said
"calls arriving over the internal service seam MUST NOT be subject to customer rate
limits", which assumed the seam is recognisable. Reading `api-client.ts` and the
internal controllers shows it is not: the **gateway forwards the end user's own
token** on all three of its calls, and `/internal/session`, `/internal/backfill` and
`/internal/messages` are all `@Accepts("user")`. Only the dispatcher presents the
platform credential.

So a gateway call resolves to `kind: "user"` with the client's `environmentId` and is
indistinguishable from customer REST traffic by principal.

**Decision: four route classes, and the rule is "count each operation once, at the
door it entered".**

| Class | Example | Limited by |
|---|---|---|
| Public customer | `/v1/channels/…/messages` | `rest`, plus `send` for a message |
| Gateway plumbing (`@Accepts("user")` under `/internal`) | `/internal/session`, `/internal/backfill`, `/internal/messages` | **nothing at the api** — the gateway limited it at the socket |
| Dispatcher (`@Accepts("platform")`) | `/internal/dispatch/*` | nothing |
| Pre-credential | `/healthz`, signup | health never; signup per source IP |

**Why the gateway's plumbing is not counted at the api.** The gateway already counted
the operation: a handshake against `connect`, a frame against `send`. Counting it again
as `rest` would charge the socket twice and make it the *expensive* transport while the
contract advertises the two as equal — and it would mean a reconnect storm silently
eating a customer's REST budget, which FR-005 describes nowhere.

**This retires the phrase "internal seam" as the exemption's basis.** The seam is not
what matters; the door is. Two of the three internal routes are user-authenticated and
would have been limited by any rule that keyed off the principal. The rule that
actually holds is the chapter's own theme said once more: one mechanism, several doors,
and each operation belongs to exactly one of them.

**Health is never limited.** Docker's healthcheck polls it every five seconds and
`docker compose up -d --wait` depends on the answer. A limiter that can refuse
`/healthz` can stop a deployment.

**Signup is limited per source IP**, reusing the `rlauth:` key family rather than
adding a mechanism. It has no tenant to key on — that is the point of it — and an
unlimited account-creation route in a chapter about limits is a gap a reader notices.
The threshold is the same configuration the auth limiter reads.

---

## R18 — Where the auth refusal is thrown, given a middleware that never throws

**`AuthenticateMiddleware` never refuses, and says so with its reason.** Its comment:
*"It NEVER throws. A request that presents nothing simply has no principal, and
pre-credential routes (signup, health) are reached that way on purpose."* The 401
comes from `CredentialGuard`, which is applied per-controller with `@UseGuards`.

FR-011 requires the auth limiter to refuse past the threshold, and T027 named the
middleware as the place. It cannot be.

**Decision: the middleware counts and marks; `CredentialGuard` throws.**

The middleware is where the failure is observable — credential present, principal
null — so counting stays there. When the count is past the threshold it sets a flag on
the request and calls `next()` as it always has. `CredentialGuard` reads the flag and
throws a `429` instead of its `401`.

**Three things this gets for free.** The middleware's invariant survives verbatim, so
pre-credential routes still reach their handlers. The guard already owns the 401 that
FR-028 wants the rate-limit refusal indistinguishable from, so both come out of one
place. And the guard already throws the object form — `code: "wrong_credential_type"`
on its 403 — so a `429` can carry `rate_limited` the same way, which is what FR-003
needs.

**What it does not cover, by design.** A route with no guard cannot refuse this way.
That is signup and health, and R17 handles both: health is never limited, signup is
limited per IP by its own check.

**Rejected: a second middleware after `AuthenticateMiddleware` that may throw.** It
works, and it puts the 429 somewhere the 401 is not, which is how two refusals that
must look alike drift apart.

---

---

## R19 — Strict env mode, and why R15's escape hatch would not have worked

**Verified by experiment rather than by reading Turborepo's documentation.** A probe
task was added declaring only `RELAY_NATS_URL`, run with that and an undeclared
variable both set, then reverted:

```text
@relay/api:probe:env: DECLARED   RELAY_NATS_URL:   nats://declared
@relay/api:probe:env: UNDECLARED RELAY_PROBE_VAR:  (undefined)
```

`turbo.json` resolves to `envMode: strict` and declares thirteen variables on
`test:integration`. **Anything not on that list reaches a task as `undefined`.**

**This defeats two of this chapter's decisions silently.** R15 designed the auth
threshold as configuration with an enforcing default precisely so a suite could raise
it. Under strict mode the child reads `undefined`, falls through to 10, and the suite
breaks exactly as R15 predicted — while appearing to have been fixed. Mailpit's
coordinates fail the same way, so the mailer would reach for `localhost:1025` when the
container is on `11025`.

**A missing variable is not an error.** It is `undefined`, and every read of it has a
`??` behind it. That is what makes this worth a research item rather than a line in a
task: the failure mode is a default quietly winning.

**The same hazard has a second home, and this project has already been bitten by
it.** `packages/e2e/src/harness.ts` forwards an explicit allowlist to the api children
it spawns, above a comment that names the incident:

> *Store coordinates are FORWARDED, never invented … That is precisely how this suite
> first failed: turbo runs tasks in strict env mode, the port variable was filtered
> out, and the harness confidently passed `localhost:5432` to an api that would have
> found the right store on its own.*

Nine variables are forwarded by name, each with the chapter that added it. This
chapter adds to both lists.

**The variables, named to the project's convention.** Full URLs with a service-side
default, because the harness comment is explicit that a harness composing its own URL
from a port becomes a second source of truth:

| Variable | Default in the service | Set by the lane |
|---|---|---|
| `RELAY_AUTH_FAILURES_PER_MINUTE` | 10 | raised by suites that submit bad credentials |
| `RELAY_SMTP_URL` | `smtp://localhost:1025` | `smtp://localhost:11025` |
| `RELAY_MAILPIT_URL` | `http://localhost:8025` | `http://localhost:18025` |

**Both files are fenced in earlier chapters** — `turbo.json` in five, `harness.ts` in
five, most recently 3.5 — so both are amendments this chapter carries.

**The rule for the next chapter that adds a variable**: `turbo.json`'s `env` list and
`harness.ts`'s `forwarded(...)` are two allowlists somebody has to remember, and
nothing fails loudly when they are forgotten. Neither is a gate. That is a defect in
the harness rather than in this chapter, and it is named here rather than fixed
because a chapter about rate limits is not where a test-infrastructure gate belongs.

---

---

## R20 — Two boundaries the platform enforces on itself, and a second store that steps outside both

**The ninth pass found nothing wrong with the documents.** It found two mechanisms the
*code* uses to enforce its own rules, neither mentioned in any spec, and a new component
that sidesteps both.

### The driver boundary is a lint rule, and it names only one driver

`eslint.config.mjs` restricts `pg` and `drizzle-orm` for every `**/*.ts` except
`services/api/src/db/**`, above a comment that states the principle rather than the
mechanism:

> *Isolation lives in data access, not in handlers (constitution I): only the
> repository layer may touch the driver.*

This chapter gives the api a **second per-tenant datastore**. The counters are keyed
`rl:{environment_id}:…`, and with `ioredis` unrestricted any controller can import a
client and read or write any environment's counter — the exact access the existing rule
exists to prevent, against a key that is per-tenant by construction.

**Decision: extend the rule to `ioredis`, ignored under `services/api/src/limits/**`.**
One entry in the same array, and it makes `store.ts` the Redis analogue of the
repository layer. Constitution I is non-negotiable and says isolation lives in data
access; a boundary enforced for one store and not the other is a boundary that holds
until the next chapter forgets.

**Why this was invisible for eight passes.** The rule is not a requirement, a test or a
gate anybody runs deliberately — it is four lines in a config file, and it works so
quietly that nothing in the spec knew it existed.

### Every long-lived resource is closed through `OnModuleDestroy`

Three api modules implement it — the outbox relay, the delivery relay, the event
consumer — `main.ts` enables shutdown hooks with a comment saying why, and every api
integration suite ends `await app.close()`.

An `ioredis` client holds the event loop open. Without a destroy hook the api's
integration suites will **hang after their assertions pass**, which is the worst
available failure shape: the tests are green and the lane never returns. This project
has spent three chapters clearing a lane; adding a resource that never closes would
undo that quietly.

**Decision: the Redis client gets a destroy hook in the shape `OutboxRelayService`
already uses.**

### And the gateway needs its own client, not fanout's

`Fanout` is a closed interface — `onDelivery`, `publish`, `subscribe`, `unsubscribe`,
`close` — and does not expose the two clients it holds. Even if it did, one of them is a
**subscriber**, and a Redis connection in subscribe mode cannot run `INCR`. The
gateway's limiter therefore opens its own client with its own `close()`, called by the
session server.

`createFanout` is also optional in the session server (`fanout?`), so a limiter riding
its lifecycle would vanish in the configurations that have no fabric — which is every
chapter-2.5 test.

**The pattern worth naming.** Both of these are *self-enforcing conventions*: a lint
rule and an interface. Neither appears in a requirement, and a component can be built
correctly against every document in this feature while violating both. The place to look
for the next one is the project's other quiet enforcers — the coverage ratchets,
`check:docs`, and whatever `scripts/` the lane runs.

---

---

## R21 — The per-IP counter is a shared resource, and this chapter would create the fifth
instance of a shape it already knows

**Two vitest configs disagree, and the difference is the finding.**
`vitest.coverage.config.mts` sets `fileParallelism: false` above a comment naming the
incident: *"Suites in one process would share a database in ways their authors did not
design for — 3.3's outbox suite learned that the hard way."*
`services/api/vitest.integration.config.mts` sets only `include`, so **the integration
lane runs files in parallel.**

Every api integration suite that asserts a `401` increments one bucket:
`rlauth:127.0.0.1:{window}`. They do it concurrently, from different workers, against
a counter in shared Redis.

**Raising the threshold works. Lowering it does not.** A suite with a high ceiling never
refuses, however polluted the count — so R15's plan for `credentials.itest.ts` holds.
But the same plan lowers the threshold in `limits.itest.ts`, which would then compare a
count filled by every other worker against a deliberately small number and refuse
requests that had nothing to do with it. Intermittently, depending on which workers ran
first.

**This is the fifth instance of one shape.** Chapter 3.7's baseline found four: a sweep
with a batch limit, a drain holding a lock, a consumer draining a growing stream on a
fixed budget, and a global `count(*)` compared against itself. All four were tests
asserting a local fact about a global operation. This chapter would have added a fifth,
by design, in the test for the very mechanism the chapter is about.

**Decision: the limiter's test gets a distinct KEY, not a distinct threshold.**

The auth bucket takes a key prefix, defaulted to the real one and overridable, and
`limits.itest.ts` sets its own. That is the fix already in this codebase twice —
`attempts.itest.ts` carries `const SUITE = "itest-attempts"` above a comment explaining
that a durable is a position in a shared stream, and chapter 3.7 gave `consumer.itest.ts`
the same treatment. There is a pattern to copy rather than a design to invent.

**And the threshold raise still has to be lane-wide.** T004a measures the whole lane's
failed authentications per minute, not one suite's, because the bucket does not care
which file produced the request.

---

## R22 — Two gates that say less than they appear to

Recorded because this feature's own reports cited one of them as evidence nine times.

**`pnpm check:docs` mirrors `docs/01` through `docs/06` only.** The script globs
`0[1-6]-*.md`. This chapter edited `docs/07-tutorial-plan.md` — twice, for the
renumbering and the split narrative — and that document is **not** in the mirror set. So
`check-docs-drift: all mirrored docs match their sources` is true and says nothing about
the file this chapter actually changed. It was never a wrong claim; it was thinner
evidence than repeating it implied.

**The coverage comment records achieved numbers that nobody updates.** The thresholds are
70% across the board — *"Set to what the constitution says, not to what the code
achieves — a threshold tuned down to pass measures nothing"* — with the current figures
noted in prose: 86.55% statements, 78.07% branches "at the time of writing". Ten new
files will move both. Chapter 3.7's quickstart inherited a nine-minute lane estimate from
3.6 the same way, and it was wrong by a factor of three by the time anyone read it.

---

---

## R23 — The connect limit and a constitution gate nothing yet keeps

**Found by reading the constitution's Quality Gates**, which eleven earlier analysis
passes never opened — they had all read the seven principles and stopped there.

> *Each service is independently deployable; deploys cause no message loss and **at
> most one client reconnection cycle**.*

R4 set connection establishment at **60 per minute per environment**. A gateway deploy
makes every connected client reconnect at once. An environment with more than sixty
connected clients cannot reconnect them inside one window, so the surplus is refused
with `Retry-After` and comes back later — a second reconnection cycle, for exactly the
event the gate names.

**The gate has a requirement id**, which this section originally failed to cite:
**NFR-REL-03**, P2, verified by Analysis — *"Deployments shall cause no message loss and
no more than a single client reconnection cycle."* The constitution's Quality Gates
restate it. A conflict recorded against a numbered requirement is worth more than one
recorded against a document.

**R26 has since raised the default to 3,000/min**, which makes the gate hold for any
environment that fits on one gateway instance. It does not make it unconditional — an
environment spanning several instances can still exceed it — so FR-045 stands, and the
drain-grace exemption remains what would make the promise hold at any size.

**And the gate has no implementation.** `CLOSE_CODES[4009]` reads "server shutdown
(drain)" and **nothing emits it**: the only occurrences in the platform are the constant
itself and the test asserting the map has four entries. There is no drain. So the
conflict is not between a limit and working code — it is between a limit and a promise
nothing yet keeps.

**That makes 4009 the fourth piece of vocabulary declared in chapter 1.3 and never
wired**, beside `rate_limited`, close code 4008 and the error envelope's `request_id`.
Three of the four are in one file. This chapter enforces one, closes one, and can now
say precisely why the other two wait: 4008 needs a quota, and 4009 needs a drain.

**Decision: record the conflict, do not paper over it, and do not build the drain.**

The constitution's own Quality Gates prescribe the handling — *"violations are recorded
and justified in the plan's Complexity Tracking table or the design is simplified"* —
and Governance requires that a conflict be *"resolved explicitly by amendment rather
than ignored"*. So it goes in Complexity Tracking with the justification, and a
requirement states that whichever chapter builds the drain must ensure the connect
limiter is not the reason a platform-initiated reconnect is refused.

**Why not fix it here.** The clean mechanism is a drain-grace marker: the draining
instance writes a short-lived flag to the shared store and the limiter skips counting
while it exists. Redis is already there and the gateway already has a client, so the
reading side is one check. But the **writing** side belongs to a drain that does not
exist, and shipping a reader for a flag nothing writes would be the fifth instance of
the habit this chapter is about — declaring a mechanism and not enforcing it, in the
chapter that names the habit.

**Why not just raise the number.** It is unbounded: the limit would have to exceed the
largest number of connections any one environment can hold, which is a number nobody
has. A limit chosen so it can never bite is not a limit, and R4's reasoning for sixty —
"a client reconnecting hard, not a client working" — stays correct for every case except
the one the platform itself causes.

---

## R24 — `docker compose up` would start an api whose limiter enforces nothing

**Constitution, Technology & Platform Constraints:** *"The full stack MUST start locally
with a single command (`docker compose up`), including a seeded demo tenant."*

The compose `api` service passes `DATABASE_URL` and `RELAY_NATS_URL` with **container**
hostnames and declares `depends_on` for postgres and nats. It has no Redis, because until
this chapter the api did not need one. With the limiter added, `RELAY_REDIS_URL` falls
through to its default of `redis://localhost:6379` — which inside that container is not
the Redis service.

**The failure mode is the quiet one.** Not a crash: FR-010 makes the tenant limiter fail
open when the store is unreachable, so a composed stack would serve every request
unlimited while reporting `X-RateLimit-Limit` and no counts. The chapter's own degraded
behaviour, permanently, because of a missing line in a YAML file.

**Correcting my own finding**: the report that raised this also said the **gateway**
service had the same gap. It does not — `gateway` already carries
`RELAY_REDIS_URL: redis://redis:6379` and `depends_on: redis`, from chapter 2.6's
fan-out. Only the api needs the wiring, plus `RELAY_SMTP_URL` for the mailer.

---

---

## R25 — The journey map's Test phase is this chapter, and it asks for two things the spec did not

**Thirteen analysis passes never opened `docs/03-journey-map.md`**, which the SRS cites
as the source of FR-RTL-06's reasoning and which `check:docs` mirrors. Its Test phase is
four lines describing this chapter's user doing this chapter's thing:

> **Doing:** Simulating network drops, testing reconnection and message ordering, load
> testing, **verifying rate limit behaviour**, checking webhook retries
> **Touchpoints:** Dev environment, **rate limit headers**, status page, docs on failure
> modes

Two of its four pain points and two of its four opportunities are this chapter's subject.

### The pain the chapter fixes, quoted

> *Rate limits that return `429` with no headers indicating remaining quota or reset
> time.*

That is FR-002, written from the other side. The chapter delivers it. Worth quoting in
the prose, because a requirement with a persona behind it reads differently from a
requirement with a number behind it.

### The one the spec understated

> *Shared dev and production quotas, so load testing risks her live environment.*
> *Fully isolated dev and production environments with separate keys and **separate
> quotas**.*

FR-006 and SC-003 cover the **counters** being independent — one environment at its limit
does not refuse another. The journey map asks for something stronger: **separate
policy**. Mai's need is to configure her dev environment differently and hammer it,
without production's limit moving.

The policy is already three nullable columns per environment, so the capability exists.
What was missing is a test that two environments of one application can carry **different
configured limits**, each enforced at its own number. T018c tested one override against
one default, which does not distinguish "the override applies" from "the override applies
everywhere".

### What a dev environment is for, and what that means for the default

Mai's Test-phase activity is *load testing*. R4 set 600/min on the reasoning that 10/s is
"generous for the integration this platform is sold for" — true for an integration, and
false for the one user the journey map says will drive a limit deliberately.

That is not a reason to raise the default. It is a reason for the chapter to say plainly
that a dev environment's limit is meant to be raised for load testing, and that this is
what FR-007's configurability exists for. A developer who hits 429 while load-testing and
cannot find out that the number is hers to change will conclude the platform is the
problem.

### The error page that does not exist, recorded rather than fixed

Constitution V: *"every error code has a reachable documentation page"*. This chapter
ships `rate_limited` as the first code a developer will receive routinely and want to look
up, and its `docs_url` points at `https://relay.example/docs/errors/rate_limited`.

**The placeholder stays.** It has been a placeholder since chapter 1.4, both
`ProtocolErrorFilter` and `service-kit` say so in comments, and a docs site is not this
chapter's to build. What changes is that the gap is now recorded: the journey map asks
for *"a documented failure-modes page: what happens on disconnect, on duplicate send, on
webhook timeout, on quota exhaustion"*, and this chapter is the one that makes the
missing page cost something real.

**A fifth thing declared and not enforced**, alongside `rate_limited`, 4008,
`request_id` and 4009 — except this one is a promise in the constitution rather than a
constant in `codes.ts`.

---

---

## R26 — The four defaults, re-derived against the SRS's own numbers

**R4 chose all four from judgement and checked none of them against a document stating
this platform's scale.** The fourteenth analysis pass read the SRS's NFR tables for the
first time and found that the connect number makes a P1 requirement unreachable. Since
one was wrong for that reason, all four are re-derived here rather than the broken one
patched.

R4's reasoning for connect was *"sixty establishments a minute per environment is a
client reconnecting hard, not a client working"*. True of a client. The limit is per
**environment**, and an environment is a tenant.

### Message sends — 600/min, and now with an anchor

NFR-SCL-03 puts platform capacity at **1,000 messages per second** aggregate, which is
60,000 a minute. 600/min per environment is **1% of that**, so a hundred environments at
their ceiling saturate the platform and the hundred-and-first is what the limit protects.

Unchanged in value, changed in status: it was a round number that felt generous and is
now a stated fraction of a stated capacity.

### REST requests — 600/min, with the overlap named

No SRS number caps a tenant's request rate directly. NFR-PRF-02's p95 under 150 ms is a
latency target, not a throughput bound. The number stays equal to the send limit, because
a REST send consumes both budgets (FR-036) and two different ceilings on one operation
would mean a client hitting one while the other says it has room.

Honest status: this is the one default with no anchor. Recorded as such rather than
dressed up.

### Connection establishment — 60/min → **3,000/min**

The old number is wrong against two P1 requirements and the arithmetic is not close.

NFR-SCL-01: **10,000 concurrent connections per gateway instance**. FR-RTM-09: **five per
user**. So one instance holds 2,000 users' worth. At 60 establishments a minute, filling a
single instance from cold takes **167 minutes**, and an environment of 5,000 users at five
connections each — 25,000 sockets — takes over six hours.

NFR-REL-03 (P2, and the constitution's Quality Gates say the same): *"Deployments shall
cause no message loss and no more than a single client reconnection cycle."* Every client
reconnects at once after a deploy; 60/min refuses all but the first sixty, and the rest
come back — a second cycle, for the event the requirement names.

**3,000/min** lets an instance's full complement re-establish inside a minute with
headroom, so a deploy stays one cycle for any environment that fits on one instance, and a
cold start reaches NFR-SCL-01's number in minutes rather than hours.

**And it is still a limit.** Its job is to stop a runaway client reconnecting in a tight
loop — that client does thousands a minute and is refused well before a legitimate fleet
is. The limit protects the platform from a broken client, not a tenant from its own users,
and R4 had those two jobs confused.

**FR-045's drain-grace exemption is still wanted**, because an environment spanning more
than one instance can still exceed 3,000, and the exemption is what makes the requirement
hold at any size rather than at one instance's worth.

### Failed authentication — 10/min per source IP, kept, with its cost stated

Nothing in NFR-SCL or NFR-PRF bears on it; FR-AUT-12 gives no number. It stays a security
judgement, and ten wrong credentials a minute from one address is still not a human
mistyping.

**The cost it carries, which R4 did not name: shared egress.** An office behind one NAT is
one source address, so ten failed logins a minute is a whole building's budget. A customer
whose staff share an IP will hit it, and the refusal is deliberately indistinguishable
from a wrong credential (FR-028), so they will experience it as "the login is broken".
Kept anyway — the alternative is a threshold high enough to be worthless against the
attack it exists for — and named so the chapter says it rather than a support ticket
discovering it.

### The table, with what each number rests on

| Operation | Default | Anchor |
|---|---|---|
| REST requests | 600/min | none — matched to the send limit so one operation cannot straddle two ceilings |
| Message sends | 600/min | 1% of NFR-SCL-03's 1,000/s aggregate |
| Connection establishment | **3,000/min** | NFR-SCL-01's 10,000 per instance ÷ FR-RTM-09's 5 per user, re-established inside one window for NFR-REL-03 |
| Failed authentication | 10/min per IP | judgement; no requirement gives a number. Cost: shared-NAT tenants share the budget |

**What this episode is really about.** Three of the four numbers were defensible and one
was not, and nothing in the process distinguished them, because all four were produced the
same way — by reasoning about a client. The fix is not the new number; it is that each
number now names what it rests on, including the one that rests on nothing.

---

---

## R27 — The error envelope's shape, and an SRS amendment

**The fifteenth analysis pass read §3 of the SRS** — the External Interface
Requirements — which fourteen earlier passes had skipped while reading §4's FR tables and
§5's NFR tables repeatedly. EIR-API-04 is P1, verified by Test, and its worked example
nested the error body's fields under an `error` key:

```json
{ "error": { "code": …, "message": …, "field": …, "docs_url": …, "request_id": … } }
```

`ProtocolErrorFilter` emits them **flat**, and has since the walking skeleton.
`service-kit`'s 404 does the same. The document and the code had disagreed about the
shape of every error response the platform sends, for fourteen chapters, and nothing had
resolved it either way.

**This chapter is the one that would have made it worse.** R5 adds `request_id` to that
envelope — a fourth field into a shape already structurally wrong — and the contract
document publishes the flat form as canonical.

**Decision: amend the SRS. `docs/04-srs.md` is now at 1.3.**

Three routes were available and the constitution's Governance names the third:
*"where it conflicts with the SRS or SAD, the conflict MUST be resolved explicitly by
amendment rather than ignored."*

| Route | Why not |
|---|---|
| Wrap the REST body to match the document | A breaking change to every error response, and CON-05 requires a new URL version for breaking changes. Far larger than a rate-limiting chapter should spend |
| Record the divergence, as FR-047 does for `docs_url` | Cheap and honest, and leaves a P1 requirement unmet with no plan to meet it |
| **Amend the document** | Taken |

**Why flat is the better shape anyway**, rather than merely the one that shipped. The
same five fields travel on the WebSocket surface inside a frame's `payload` (EIR-WS-02),
and `ProtocolErrorFilter`'s own comment gives the reason — *"one error shape, one home …
so the REST surface and the WebSocket surface cannot drift apart"*. Nesting the REST body
under `error` would make the two differ in **two** ways: the transport wrapper, which is
unavoidable, and the field container, which is not.

**What the amendment changed**: EIR-API-04's text now requires the five fields top-level
and makes `request_id` required rather than merely present in an example; the example
lost its wrapper; Appendix D records revision 1.3 with the reason; the version line moved
from 1.0 to 1.3, which is its own small finding — the document had been amended twice
without its version being updated.

**The mirror was re-synced.** `docs/04-srs.md` is one of six documents
`relay-tutorial/scripts/sync-docs.sh` copies into `content/docs/`, and `check:docs`
compares them. Amending the source without syncing would have broken a gate that had
passed for fifteen passes — which R22 already noted says less than it appears, since it
covers `01`–`06` and not the tutorial plan.

---

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
