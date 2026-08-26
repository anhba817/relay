# Research — chapter 3.18, the message that never arrived

Nine questions, each answered by reading the repository rather than reasoning about it. Chapter
3.17 had five wrong task premises before implementation and three more found during it; these
were measured first.

## R1 — the blast radius

    the api's send path                    1 file, services/api/src/messages/messages.service.ts
                                           or its controller — the publish site (R2)
    the api's module wiring                1 file, to provide a publisher
    a shared subject grammar + payload      1 file in packages/protocol (R3)
    the gateway's fanout.ts                 1 file, to consume the shared grammar rather than
                                            define it
    tests                                   3-5 files: an api-side publish test, a cross-service
                                            delivery test, and the outsider

**Small, and that is the finding.** The fan-out exists, the subject grammar exists, the gateway
subscribes already, and `fanout.itest.ts:89` already proves cross-instance delivery works. What
is missing is one publisher. Compare chapter 3.17's 35 files: this chapter's risk is not volume.

## R2 — where the publish goes

**Decision**: on the send path, after the write commits and after the response is formed —
`messages.service.ts` or the controller, not the outbox consumer.

**Rationale**: `docs/05-sad.md` decides it twice. Line 138 draws `api -- "publish fan-out" -->
redis` as a direct edge. Line 254 fixes the ordering: *"Ack after commit, never before
(FR-MSG-05). The Redis fan-out happens after the ack; a recipient may see the message
milliseconds after the sender's ack, never before durability."*

**Alternatives considered**:

- **The outbox consumer.** Its handler is `createRecorder`, which records rather than delivers,
  and the seam is right there. Rejected: it adds the outbox relay's poll interval to every
  message's delivery latency, and it contradicts a drawn edge. Worth measuring during the
  chapter — if the relay's latency turns out to be small, the architectural argument (state and
  its events commit atomically, ADR-06) is genuinely stronger. Recorded so the chapter can say
  why it did not take the cleaner-looking path.
- **Inside the write transaction.** Rejected by FR-MSG-05 and by the SAD's ordering: a publish
  before commit can deliver a message that then rolls back.

## R3 — the subject grammar has to move, and there is a precedent

**Decision**: move **`subjectFor(channelId)` only** from `services/gateway/src/fanout.ts` into
`packages/protocol`.

**`DEFAULT_REDIS_URL` does not move** — corrected during analysis. It is declared **three times**
in this repository: `services/api/src/limits/store.ts:44`, `services/gateway/src/fanout.ts:27`, and
`services/gateway/src/limits.ts:22`. Moving one of three copies into a shared package leaves a
shared definition *and* two locals, which is worse than three locals — a reader cannot tell which
is authoritative. It is also deployment configuration rather than protocol, and `packages/protocol`
holds wire contracts. A subject string is a wire-level name; a connection URL is not.

**And the api needs no new configuration at all.** `limits/store.ts:86` already reads
`process.env["RELAY_REDIS_URL"] ?? DEFAULT_REDIS_URL`, the same variable `createFanout` reads. The
publisher takes its URL the way the api's own limiter already does. **The payload type does not move — it
is already there.** `messageSchema` is `frames.ts:15`, `Message` is `frames.ts:145`, and
`fanout.ts` imports both from `@relay/protocol` today. The first version of this research said the
payload type had to move; reading the file's import line corrected it.

`createFanout` itself stays in the gateway. Moving it would put `ioredis` inside a package that
has exactly one dependency (`zod`) or inside `service-kit`, which has **none** — a client with a
socket does not belong in either. What has to agree between two services is the subject string,
and that is what moves.

**Rationale**: the api cannot import from the gateway — they are separate services and
`services/api/package.json` does not depend on the gateway. Both depend on `@relay/protocol`.
And this exact move has a precedent in this repository: chapter 3.4 moved the JetStream subject
grammar into `@relay/protocol` with the reason stated in the file — *"the subject grammar moved
to @relay/protocol in chapter 3.4, because a consumer needs it too and both sides must agree on
it."* Two publishers on one subject is the same argument, one subject over.

**Alternatives considered**:

- **Duplicate the grammar in the api.** Rejected — two definitions of one subject is a drift
  waiting for a chapter to find it.
- **Move `createFanout` into `packages/service-kit`.** It already provides `Logger`, so the import
  would be tidy. Rejected: service-kit has zero dependencies and five exports (`createLogger`,
  `newRequestId`, `serve`, and two types). Adding a Redis client changes what that package *is*,
  and the api needs the publisher half only.
- **Have the api import the gateway's `createFanout`.** Not possible: separate services, and
  `services/api/package.json` does not depend on the gateway.

The consequence is a small duplication — the api writes its own ten-line publisher — and R10 is
the reason that is the right trade rather than a reluctant one.

## R4 — what the api's publisher must mirror, exactly

The gateway's publisher is guarded:

    if (!committed.duplicate && committed.text !== null) { await fanout?.publish({...}) }

Both conditions are load-bearing and both are documented in place:

    !committed.duplicate     a recognised retry wrote no row. "2.3 made the retry safe for
                             storage; that did not make it safe for delivery, and a client
                             that retries on a flaky link would otherwise put the same message
                             on every member's screen twice."
    text !== null            "a tombstone recovered by an old key is not a creation."

**The api's publisher must carry both**, and the payload is six fields: `id`, `channel`, `seq`,
`user`, `text`, `created_at`. Chapter 3.17 made `user` non-null for every new message, which is
what makes a REST-sent row publishable at all — `messageSchema.user` is `z.string().min(1)`.

**A third condition is new to this path**: the gateway publishes only for sends it accepted
itself, so it never had to ask whether the send was refused. The api's publisher runs after a
send that may have thrown, and FR-008 requires nothing be published then. The natural shape is
publishing only on the success path rather than in a `finally`.

## R5 — membership at delivery, and where it is NOT checked

    registry.subscribersOf(channelId)      session.ts:175 — the recipient lookup
    fanout.itest.ts:102                    "does not deliver channels an instance has no
                                           member of" — the subject is the filter

**Delivery filters by SUBSCRIPTION, not by a membership read.** An instance subscribes to
`chan:{id}` while it holds a connection whose session named that channel, and the session's
channel list comes from `POST /internal/session` at connect time (FR-RTM-01's other half, cited
in `internal.ts:120`).

**So FR-RTM-10's five seconds is not obviously met, and this chapter must not assume it is.** If
a user is removed from a channel while their socket is open, the subscription persists until
something re-reads membership. Chapter 3.15's `T153` found that a ban's effect on an open socket
was a third answer nobody had written down; this is the same question for a membership change,
and it becomes reachable on a second path once REST sends deliver.

**This is the chapter's largest open risk** and the reason FR-013 forbids assuming the socket
path's answer covers the REST path. It may turn out that neither path meets FR-RTM-10, in which
case the honest outcome is a recorded gap rather than a quiet claim.

## R6 — the api's Redis client

`services/api/src/limits/store.ts` already imports `Redis` from `ioredis`, the same library
`fanout.ts` uses, and already handles the failure mode: *"ioredis emits `error` on an
EventEmitter with none attached, which Node turns"* into a crash. So the api needs no new
dependency and the error-handling pattern exists in the api's own code.

**The api needs the publisher half only.** `createFanout` builds two clients — a publisher and a
subscriber — because a subscribed ioredis connection cannot issue ordinary commands. The api
never subscribes, so it takes one client and a narrower interface than `Fanout`.

## R7 — cross-instance delivery is already tested

`fanout.itest.ts:89` — *"delivers a message published on one instance to a subscriber on
another"*. FR-RTM-02 holds at the **fabric** layer today; what has never been tested is the api as
the publisher.

**The sentence that followed this in the first draft was wrong**, and analysis caught it: *"SC-002's
test is that test's shape with a different publisher, not a new fixture."* It is not. `instance()`
in that file builds two `Fanout` objects and nothing else — the file's own line 11 says *"Two fabric
clients stand in for two gateway instances"* — so it has **zero gateway boots and zero socket
opens**. There is no socket in it to assert on.

**The first version of this section then made a second error, caught one pass later.** It said
*"no fixture boots a real api with a real gateway"*, on the strength of a `grep` for `NestFactory`
and `AppModule` in `services/gateway/src` that returned nothing. **The harness spawns the api's
built output instead of importing it**, so the mechanism searched for was not the mechanism in use.
The true census:

    services/gateway/src/session.itest.ts   REAL api, SPAWNED from services/api/dist/main.js
                                            (:106 startApi — a real pool, a real environment,
                                            user, channel, membership and key). Its own error
                                            message: "the api is not built — run `pnpm build`
                                            before this lane (the suite talks to the real
                                            service, not a stub)"
                                            2 sockets · NO FAN-OUT WIRED (:224 passes none,
                                            and session.ts:125 declares `fanout?: Fanout`)
    services/gateway/src/resume.itest.ts    stubbed api (:21) · 2 gateway instances · 6 sockets
                                            · fan-out wired (:65, :76) · :123 already publishes
                                            from a second client on the same subject
    services/gateway/src/fanout.itest.ts    fabric only — 0 gateway boots, 0 socket opens
                                            (:11 "Two fabric clients stand in for two
                                            gateway instances")
    services/api/**.itest.ts                no suite opens a socket; three reach a real Redis
    packages/outsider/                      RELAY_API_URL and RELAY_WS_URL, sealed, against a
                                            platform it did not start

**So a full cross-service fixture already exists**, and it is one wiring change from hosting this
chapter's end-to-end test: `session.itest.ts` has the real api and the real socket, and lacks only
the fan-out. That is a shared-fixture change and carries 3.17's T040b risk, which is why it is its
own task rather than a line inside another.

Recorded at length because the error is the fifth of its kind in this project: **a pattern matching
the examples in front of me rather than the set the rule names.** The question that would have
worked is *"how does any gateway suite obtain an api?"* — not *"does any gateway suite import
Nest?"*

## R8 — what happens today if a publish throws

The try/catch is **inside `publish`**, not at the call site: it logs `fanout.publish_failed` and
resolves normally. *"Delivery is allowed to fail; the message is already durable and 2.7's resume
will find it. Log and move on."* The SAD agrees: *"Redis lost → presence + fan-out pause. Gateways
buffer briefly, reconnect clients; Postgres unaffected."*

**So `publish` never rejects, and that has a consequence for testing.** A test that asserts "the
send still succeeded when the fan-out was down" passes identically whether the publish failed and
was swallowed or succeeded outright — it cannot tell those apart, so it proves nothing about
FR-010. The assertion that carries the requirement is on the **log line**, which is why FR-011
asks for observability and not just for survival. This is 3.17's T086 shape: a test whose success
is compatible with the mechanism being absent.

## R9 — the governing documents, and why there is no amendment

    FR-RTM-01   P1   "A connected client shall receive messages for every channel of which
                     it is a member, without per-channel subscription."     UNMET for REST
    FR-RTM-02   P1   delivery across gateway instances                      met at the fan-out
    FR-RTM-05   P1   six event kinds                                        only creation is
                                                                            producible
    FR-RTM-10   P1   no events after membership lapses, within 5 s          see R5
    docs/05-sad.md:138, :254   the edge and its ordering                    drawn, never built

**No SRS clause needs amending, and that is worth a sentence in the chapter.** Chapter 3.17's gate
was an SRS amendment because the SRS had no bot concept; principle VI is satisfied here by citation
of FR-RTM-01. A reader arriving from 3.17 will look for an SRS amendment and there is none.

**The SAD is a different matter, and the first draft of this section was wrong about it.** It said
*"nothing needs amending"* on the strength of line 138. Ten lines above §5.1's ordering bullet, the
same document draws the publish as `G->>G` — the gateway — and models no REST send:

    :138   component view    api -- "publish fan-out" --> redis        the api publishes
    :248   sequence view     G->>G: publish to Redis chan:{...}        the gateway publishes
    :254   the bullet        "The Redis fan-out happens after the ack" unconditional, and
                                                                      FR-005 now splits it

Reading the identifier answered *is the edge drawn*. It never answered *does the document agree
with itself* — the second of CLAUDE.md's three mechanisms, applied three passes late to the one
document this chapter's justification rests on. `05-sad.md` is also mirrored into
`relay-tutorial/content/docs/`, so the edit is not done until `pnpm sync:docs` has run.

**The one thing to verify before writing a requirement about FR-RTM-05**: measured, only message
creation has a producer. `message.updated` and `membership.changed` have zero producers outside
tests, nothing writes `messages.edited_at` or `messages.deleted_at`, and typing has no frame in
the union. The chapter delivers one event kind because one is all that exists.

## R10 — the hazard the api's own limiter already fixed, and the gateway has not

`createFanout` builds both clients with `new Redis(url)` — **default options, and no `error`
listener on either.** Two other files in this repository build Redis clients, and both do it
differently, with the reason written down. `services/api/src/limits/store.ts`:

    lazyConnect: true, maxRetriesPerRequest: 0, connectTimeout: 1_000
    redis.on("error", () => {});

and its comment: *"FAILING OPEN IS NOT FREE IF IT FAILS SLOWLY, and the first version of this file
was slow. With the store gone, every command waits out its connect timeout before giving up — so
each request paid a second or more, twice… an outage that instead adds seconds to every request
has refused it in a slower way, and NFR-PRF-02 asks for a p95 under 150 ms."* On the listener:
*"Without a listener ioredis emits `error` on an EventEmitter with none attached, which Node turns
into an unhandled exception and the api dies for the thing it was designed to survive."*
`services/gateway/src/limits.ts:104` attaches the same listener.

**Two findings, and they point in different directions.**

The first is about the api's new publisher: it sits on a request path with a 150 ms budget, so it
must take the limiter's options rather than the fan-out's. Copying `createFanout`'s client into the
api would import a hazard the api's own code fixed two chapters ago — a dead Redis turning every
send slow instead of merely undelivered. This is the concrete reason R3's small duplication is
right: the api's publisher is not the gateway's publisher, and the difference is the request path.

The second is about the gateway, and it is a **claim to verify, not a conclusion.** By the
limiter's own reasoning, a `new Redis` with no `error` listener should take the process down when
Redis is unreachable, and `createFanout` has none. There is also **no test anywhere for a dead
fan-out** — `grep` for a fan-out down/gone/failing case in the gateway's integration suites
returns nothing. Whether the gateway actually dies depends on details this research did not
measure (ioredis's retry schedule, whether `fanout` is constructed at all in the failing path), so
the task is to try it: stop Redis, send on a socket, see what happens to the process.

If it does die, that is a pre-existing defect surfaced by this chapter rather than caused by it,
and it belongs to the chapter's argument either way — the fabric documented as *"permitted to be
lossy"* would have been fatal instead of lossy, in the one file whose comment explains why loss is
acceptable.
