# Research — chapter 3.8, "Limits you can see coming"

Phase 0. Sixteen items. R3 is the chapter's central decision and the spec
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
| **Rate limiting subtotal** | **28** |
| Mailer + tests | 2 |
| Notification relay + tests | 2 |
| `repository.ts` claim (already counted above) | 0 |
| Notifications module, wiring | 2 |
| Integration suite for notifications | 1 |
| `package.json` (nodemailer) | 0 (counted) |
| **Transport subtotal** | **7** |
| **Total** | **~35** |

**For comparison, measured rather than remembered**: chapter 3.5 shipped 39 fences
against a budget first estimated at 22 and ran 4,952 prose words; chapter 3.6
shipped 21 and ran 5,273. The bound is 2,000–4,000.

**Finding: the fences will not fit inside the word bound, and the transport is the
separable seven.** The rate-limiting half is one mechanism with one argument — the
failure directions.

**The estimate moved, and upward.** It was 23 and 30 when first written; three
analysis passes added five fences to the limiter half, all of them consequences of
the gateway not being the api — its own counter helper, the limits reaching it on the
internal contract, and the `Connection` holding them. **28 for one half is above
chapter 3.6's entire 21.** The finding is stronger than when it was written, which is
the opposite of how estimates usually move, and it is the number T058's gate measures
against. The transport's seven
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

## R11 — Which bucket a REST send decrements

**Raised by analysis, not by the plan.** Three buckets are defined — `rest`,
`send`, `connect` — and a `POST /v1/channels/{id}/messages` is both a REST request
and a message send. Nothing said whether it decrements one, the other, or both,
and FR-002 describes **one** set of headers. A client reading `Remaining: 599`
could not tell which allowance it had just read.

**Decision: both are decremented, and the headers report whichever has fewer
remaining.** Ties report `rest`.

**Why both.** The alternative — `send` counts socket frames only, `rest` counts
HTTP — is tidier and lets a customer double their send rate by using both
transports at once. The limit exists to bound sustained load on the platform, and
a bound a client can lift by opening a socket is not a bound. A message costs the
same downstream whichever door it came through.

**Why the nearest limit.** The headers can only describe one bucket, so they must
describe the one that will refuse first — that is the only value a client can
schedule against. `X-RateLimit-Reset` is that same bucket's reset, and a refusal's
`Retry-After` comes from the bucket that actually refused. Reporting the *higher*
remaining would be a header that lies by omission: a client with `Remaining: 400`
on `rest` and `12` on `send` needs to hear 12.

**The refusal names which limit was hit** in its `message`, because "too many
requests" and "too many messages" are different things for a client to fix — one
means batch, the other means slow down. The code stays `rate_limited` (the
protocol constant); the message carries the distinction, and neither names a
credential (NFR-SEC-06).

**This is what FR-008 was rewritten to catch.** A limiter counting requests and one
counting messages are indistinguishable on single-message traffic. With both
buckets live, a batch of ten messages in one request decrements `rest` by 1 and
`send` by 10 — and a test that sends batches is the only thing that can tell the
implementation got it right.

**Alternatives considered.** One bucket for everything — rejected: it cannot
express "few large batches" and "many small requests" as different loads, which is
the distinction the two numbers exist for. Reporting all three buckets in
repeated headers — rejected: `X-RateLimit-*` has no established multi-value
convention and a client parsing the first occurrence would read an arbitrary one.

---

---

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

**This makes FR-009 and FR-012 interact**, which is worth a section in the chapter:
the same request is simultaneously trusted (do not throttle it) and untrusted (do
not believe it is the origin). The address is forwarded on the internal contract
rather than read from a header a caller could set, because chapter 3.2 removed
exactly that pattern — a header the caller asserts is a header the caller can forge.

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
The real collision is `credentials.itest.ts`, which T025c has to touch to raise the
auth threshold.

**The rule that comes out of all three mistakes**: check the post-series title list
before generating a fence, and match on the full path rather than the basename.

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
