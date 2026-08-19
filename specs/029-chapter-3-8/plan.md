# Implementation Plan: Tutorial Chapter 3.8 — "Limits you can see coming"

**Branch**: `029-chapter-3-8` | **Date**: 2026-08-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/029-chapter-3-8/spec.md`

## Summary

Per-environment fixed-window counters in Redis on REST requests, message sends and
connection establishment, with `X-RateLimit-Limit`, `-Remaining` and `-Reset` on
every response rather than only on the refusal; `429` with `Retry-After` when the
allowance is gone; per-IP limiting on failed authentication. Plus the email
transport chapter 3.6 deferred, which turns out to be the outbox pattern's third
instance over a table that already has the right shape.

**The chapter's argument is the failure direction.** Redis holds the counters and
SAD §6.3 says nothing in Redis is a source of truth, so the tenant limiter fails
open — a cache outage is not a reason to refuse paid traffic. The same reasoning
applied to the limiter guarding failed logins gives the opposite answer, because
failing open there is not a degradation but a hole. Research R3 settled the third
answer the spec left open: an in-process fallback with the same threshold, so the
guarantee weakens from N per window per fleet to N per window per instance — a
small multiple rather than infinity.

**Two findings changed the shape of the work.** Research R5 found that
constitution V's four-field error envelope has been three fields since chapter
1.3, above a comment promising `request_id` would arrive "in Part 2, when a gateway
exists to mint one". It never did. That makes three pieces of vocabulary declared
and unenforced — `rate_limited`, close code 4008, and the fourth field — and the
chapter has to close the third one because FR-003 requires it in the 429 body.

**A third finding came from `/speckit-analyze` rather than from planning, and its
first answer was wrong.** Nothing said which bucket a `POST /messages` decrements.
R11's first answer justified two buckets with a batch send — ten messages in one
request — and **there is no batch send**: both `sendMessageBodySchema` and
`messageSendSchema` carry a single `text`. The sixth pass caught it. The answer that
survives is a cross-transport one: the send limit counts messages wherever they
enter, so a client cannot lift its message budget by switching transport, and the two
counters diverge the moment the socket is used. FR-036, FR-036a, T018a and T018b.

Research R10 put a number on the size risk the spec flagged: about **35 fences**,
**28 of them the limiter half alone**, against 21 in chapter 3.6 which already ran
5,273 words on a 2,000–4,000 bound. The estimate started at 30 and three analysis
passes moved it up, every addition a consequence of the gateway not being the api.
The recommendation is that the transport's seven fences want their own chapter. The
plan does not act on that — the scope was chosen deliberately — but it orders the
phases so the transport is last and lifts out cleanly if the word count says so.

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22, unchanged (constitution VII,
ADR-01).

**Primary Dependencies**: NestJS 11 for the api; `ioredis` 6, already a gateway
dependency and **new to the api**; `nodemailer` for SMTP, the first new runtime
dependency since chapter 3.4's `nats` client; `ws` in the gateway, unchanged.

**Storage**: Redis for the counters, fixed window with the TTL doing the cleanup.
The key is `rl:{environment_id}:{operation}:{window}` — SAD §6.3 specifies
`rl:{env}:{bucket}`, and this **extends** that shape rather than matching it: the
operation and the window go in the key so one `INCR` reaches the right counter and
the key expires itself. Same prefix, same store, same ephemerality. Postgres for
the limit policy, because a policy is not ephemeral and losing it must not grant
unlimited traffic. One migration, `0008`, adding a nullable per-environment
override.

**Testing**: Vitest, two lanes. Unit for the bucket arithmetic and the fallback
counter, which are pure. Integration against the compose stores for the middleware,
the gateway refusal, and the mail path. Mailpit's HTTP API is what makes the email
assertions real — a test reads what was received rather than what the sender
believed it sent.

**Target Platform**: Linux, the compose stack plus one new container.

**Project Type**: Two deliverables in one feature, as every chapter in this series
is — a change to `relay-platform` and a chapter in `relay-tutorial` that shows it.

**Performance Goals**: Two Redis round trips per limited request at most
(`INCR`, and `EXPIRE` only on the first increment of a window). NFR-PRF-02 puts
REST write p95 under 150 ms and the limiter must not be a visible fraction of it.

**Constraints**: The limiter may not become a source of truth (constitution IV).
It may not throttle the internal service seam (FR-009). Its failure may not take
the platform down (FR-010) and may not open a brute-force window (FR-011). The
mail path may not affect message delivery, API availability or webhook dispatch
(FR-024).

**Scale/Scope**: ~30 fenced files, one migration, two new runtime dependencies, one
new container. See the size finding above and research R10.

## Constitution Check

*GATE: passed before Phase 0. Re-checked after Phase 1 below.*

| Principle | Bearing on this chapter | Verdict |
|---|---|---|
| **I. Tenant isolation is correctness** | Counters are keyed by environment and FR-006 requires two environments of one application to be independent. A shared counter would be a cross-tenant leak of a new kind: one tenant's traffic refusing another's. | Pass — tested by SC-003 |
| **II. No acknowledged message lost** | A `429` is a refusal, not a loss: nothing was acknowledged. The limiter must refuse *before* the write, never after — a request that committed and then returned 429 would be exactly the violation. | Pass — ordering is the requirement |
| **III. Two data paths, never crossed** | The notification transport is a third path and must fail alone (FR-024). The argument is the same one 3.6 made for analytics: not less important, just not coupled. | Pass — research R8 |
| **IV. Single writer, single source of truth** | The counter is in Redis and is deliberately not authoritative — which is *why* it fails open. The policy is in Postgres, which is. | Pass, and this principle is what decides R1 and R3 |
| **V. API-First, developer-first** | FR-002's headers on successful responses are this principle in header form: usage is observable, not a surprise. And R5 found the four-field error envelope has been three fields since 1.3 — a live violation this chapter closes. | **Currently violated by the platform**; closed here |
| **VI. Requirement-driven, test-verified** | Every FR maps to a test below. NFR-MNT-02's sabotage discipline applies, and SC-007 names the mutation that matters: making the auth limiter fail open, because R3's decision has no code of its own. | Pass |
| **VII. Boring by design** | Two new dependencies and a new container, all three needing justification. `ioredis` is already in the workspace. `nodemailer` avoids hand-rolled SMTP. Mailpit exists only in `compose.yaml`, never in a deployment, and is the only way to assert on what an email contains. | Pass with the justifications recorded in research R9 |

**No gate fails.** The one constitution violation found is pre-existing, is in the
platform rather than in this plan, and is closed by this chapter's FR-003 and R5.

## Project Structure

### Documentation (this feature)

```text
specs/029-chapter-3-8/
├── plan.md              # This file
├── spec.md              # 42 FR, 4 user stories, 12 SC
├── research.md          # Phase 0 — R1…R18
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1 — V0…V11
├── contracts/
│   └── limits.md        # Phase 1 — headers, statuses, close behaviour
├── checklists/
│   └── requirements.md  # 16/16
└── tasks.md             # Phase 2, /speckit-tasks
```

### Source code (repository root)

```text
relay-platform/
├── compose.yaml                                    # + mailpit
├── packages/
│   ├── protocol/src/frames.ts                      # + request_id on the error frame
│   └── service-kit/src/index.ts                    # + request_id in the 404 shape
├── services/
│   ├── api/
│   │   ├── migrations/0008_limit_policy.sql        # new
│   │   ├── package.json                            # + ioredis, nodemailer
│   │   └── src/
│   │       ├── app.module.ts                       # middleware order
│   │       ├── protocol-error.filter.ts            # + request_id
│   │       ├── auth/authenticate.middleware.ts     # failed-auth counting
│   │       ├── db/{schema,repository}.ts           # policy + notification claim
│   │       ├── limits/                             # new
│   │       │   ├── bucket.ts        bucket.test.ts
│   │       │   ├── store.ts
│   │       │   ├── fallback.ts      fallback.test.ts
│   │       │   ├── rate-limit.middleware.ts
│   │       │   └── limits.itest.ts
│   │       └── notifications/                      # new
│   │           ├── mailer.ts        mailer.test.ts
│   │           ├── notification-relay.ts
│   │           ├── notifications.module.ts
│   │           └── notifications.itest.ts
│   └── gateway/src/session.ts, session.test.ts     # handshake + frame limiting
└── vitest.coverage.config.mts                      # ratchets for the new files

relay-tutorial/
├── app/(en)/part-3/chapter-08/limits-you-can-see-coming/{page.mdx,figures.ts}
├── app/(vi)/vi/part-3/chapter-08/limits-you-can-see-coming/{page.mdx,figures.ts}
├── lib/tutorial.ts                                 # done during /speckit-specify
└── fences/post-series.md                           # only if something needs it
```

**Structure decision**: the limiter is a directory inside the api rather than a
package, because nothing else consumes it — the gateway limits its own two things
against the same Redis with its own small helper (`services/gateway/src/limits.ts`),
and inventing a shared package for two call sites is the kind of abstraction
constitution VII asks to be justified.

**The gateway's half has a constraint the api's does not**: it has no database
client and must not gain one, so the limits it enforces ride the internal
authentication response it already makes and are cached on the `Connection` for its
lifetime (research R12). It also has no request id to put in the field R5 requires,
so it mints one (research R13). Neither was visible until the second analysis pass,
and both are properties of the gateway's deliberate poverty rather than oversights
in it.

**And the exemption cannot key off the principal.** The gateway forwards the **end
user's** token on all three of its api calls, so they resolve to `kind: "user"` with
the client's environment — indistinguishable from customer REST traffic. Only the
dispatcher carries the platform credential. The rule that actually holds is *count each
operation once, at the door it entered* (research R17), and the refusal for an
over-threshold authentication is thrown by `CredentialGuard` rather than by a
middleware that never throws (research R18). The split inside `limits/` follows chapter 3.7's division and for the
same reason: `bucket.ts` and `fallback.ts` are pure and unit-testable with no
store, no socket and no clock; `store.ts` and the middleware hold the I/O.

## The pieces, in the order they should be built

Phase order is doing real work here — see the size finding — so it is stated
before the task shapes.

1. **The bucket arithmetic and the policy.** Pure functions and one migration.
   Nothing observable yet, everything unit-tested. This is where the fixed-window
   decision (R1) becomes code and where the burst-across-boundary consequence gets
   a test that documents it rather than a comment that claims it.
2. **The tenant limiter on the REST path.** Middleware after authentication,
   headers on success, `429` with `Retry-After`. The first thing a reader can see.
   The internal-seam exemption (FR-009) lands here, tested, because a limiter that
   throttles the dispatcher is a platform stall.
3. **The error envelope.** `request_id` added everywhere, not only on the 429
   (R5). Done as its own step because it touches three files fenced in three
   earlier chapters and its blast radius is every error response the platform
   sends — the compiler will find the construction sites, and that is the point of
   `strictObject`.
4. **The failure directions.** Fail open for tenants, in-process fallback for auth,
   the degraded header shape from R6, one rate-limited log line. This is the
   chapter's argument and it comes after the mechanism exists to degrade.
5. **The gateway's two limits.** First the three things it needs and does not have:
   the limits on the authentication response, its own counter helper, and a request
   id for its error frames. Then `429` before the handshake, `rate_limited` on an
   open connection, and close code 4008 left deliberately unused for chapter 3.9.
6. **The notification transport.** Last, and separable. The outbox a third time
   over a table that already has `delivered_at`: claim, send, mark. Mailpit in
   compose, the unaddressable-recipient branch, and the backlog 3.6 accumulated
   draining as ordinary undelivered work.
7. **The chapter, then the translation, then close-out.**

**Why 3 sits between 2 and 4** rather than at the end with the other bookkeeping:
step 2 ships the `429` body, and shipping a three-field body and then widening it
would mean the chapter's own fences disagreeing with each other across two
sections.

**Why 6 is last and what "separable" buys.** If the prose lands over the bound,
steps 1–5 are a complete chapter about one mechanism and step 6 lifts out into its
own chapter without unpicking anything: it shares no file with the limiter except
`repository.ts` and `package.json`. Ordering it last means that decision can be
made with the word count in hand instead of predicted now.

## Phase 2 preview — how tasks will be shaped

- **Setup and baseline first, and measured rather than assumed.** Chapter 3.7's
  baseline found a pre-existing failure that would have been blamed on its own
  work, and four more turned up during its twenty runs. The baseline task records
  exit codes and the lane's flake count before anything changes.
- **Tests before the mechanism**, per phase, and *watched to fail*. Chapter 3.7's
  T007 exists because a regression test nobody has seen fail is a regression test
  nobody has checked.
- **The sabotage battery gets its mutations named in the tasks**, including the one
  SC-007 requires: make the auth limiter fail open. R3's decision is a prohibition
  with no line of code behind it, and chapter 3.7 shipped its central decision
  untested until a mutation said so.
- **`git commit` before the battery.** Its revert step is `git checkout --`, which
  silently ate an uncommitted fix during chapter 3.6.
- **The word count is measured at the point the transport is still liftable**, not
  at the end. That is the whole reason for the phase order.
- **The fence budget is checked against R10's 30** rather than counted afterwards.
  3.5's budget was estimated at 22 and shipped 39, and nobody noticed until the
  battery.

## Traceability

| Requirement | Where it is decided | How it is verified |
|---|---|---|
| FR-001, FR-006 | research R1, R4 | `limits.itest.ts`; SC-003's two environments |
| FR-007 | research R4 | T011a — an override set to 2 refuses the third request while a default environment is untouched |
| FR-002 | research R1, R11 | headers asserted on 200s, not only 429s |
| FR-014 | research R6 | T025a — `Limit` present, `Remaining` and `Reset` absent, store down |
| FR-003 | research R5 | the 429 body's four fields |
| FR-004, FR-005 | research R7 | `session.test.ts`; the pre-handshake 429 |
| FR-037 | research R12 | T034a — a configured connect limit enforced with no db client, and a mid-connection change that does not apply until reconnect |
| FR-038 | research R13 | T031c; every `error` frame carries an id |
| FR-039 | research R14 | T030b — ten client addresses counted as ten, not as one gateway |
| FR-008, FR-036, FR-036a | research R11, rewritten after the sixth pass | T018a — five REST sends plus five socket frames leave send at 10 and rest at 5; T018b — a socket send counted once, by the gateway, against the shared key |
| FR-009 | research R17 | T016a the dispatcher, T016b **the gateway** (user-authenticated, so a principal-based exemption misses it), T016c `/healthz` |
| FR-040 | research R18 | T027a — the `429` thrown from the guard, not the middleware that never throws |
| FR-041 | research R17 | T027b — signup per source IP |
| FR-010, FR-011, FR-015 | research R3 | Redis stopped mid-run; both halves in one outage |
| FR-012 | research R2, R4, R15 | per-IP failures past the threshold; T004a measures what the lane already produces, T025b/c make the threshold configuration |
| FR-013 | research R6 | one log line, no credential, rate-limited |
| FR-016…FR-020 | research R8 | `notifications.itest.ts` against Mailpit's API |
| FR-021 | research R9 | the received message read, not the sent one |
| FR-022, FR-023 | research R9 | the null-email branch |
| FR-024 | research R8, constitution III | mail server down, everything else up |
| FR-025 | research R9 | `compose.yaml` |
| FR-026…FR-029 | research R3, R5, R7 | the chapter's own sections |
| FR-030…FR-032 | research R16 | `pnpm check:fences`; T061a-c handle the post-series exception |
| FR-033…FR-035 | the renumbering note in research | done during `/speckit-specify`; verified at close-out |

## Constitution re-check, after Phase 1

Re-run against the design rather than against the spec. Two entries changed.

| Principle | Post-design verdict |
|---|---|
| I. Tenant isolation | Pass. The key is `rl:{environment_id}:…` and the data model makes the environment part of the key rather than a filter applied to a shared counter — the difference between isolation by construction and isolation by remembering |
| II. No acknowledged message lost | Pass, and now with a stated ordering: the limiter runs in middleware, before any handler, so a refused request never reached a write. A limiter placed after the handler could return 429 for a message that had already committed, which is the violation |
| III. Two data paths | Pass. The notification relay is a background loop, so a dead mail server cannot fail a customer's request |
| IV. Single writer | Pass, and this principle is doing the most work in the design: it is the reason the counter is allowed to be lost (R1), the reason the policy is in Postgres rather than Redis (R4), and the reason the tenant limiter fails open (R3) |
| V. API-first | **Changed from "violated" to "closed by design".** R5's `request_id` is added to the envelope everywhere. The remaining half of "usage is observable" — a dashboard view — has no dashboard to live in and is named out of scope |
| VI. Test-verified | Pass, with one thing to watch. R3's decision is a prohibition, so `fallback.ts` existing does not prove the auth limiter refuses to fail open. V10's third mutation is the only check on it |
| VII. Boring by design | **Changed from "pass with justifications" to "pass, and the justifications got weaker under scrutiny."** Three additions is a lot for one chapter. `ioredis` is unarguable. `nodemailer` and Mailpit both belong to the transport half — which is also the half R10 recommends splitting out. If the split happens, this chapter adds one dependency and no container, and the entry reads better |

**The re-check found one thing the pre-check did not.** Constitution VII's cost and
R10's word-count finding point at the same seam: the transport carries both new
dependencies and the new container as well as the seven separable fences. That
strengthens the split recommendation without changing the decision, and it is why
the phase order keeps it available.

---

## Complexity Tracking

| Violation | Why needed | Simpler alternative rejected because |
|---|---|---|
| A fifth container in `compose.yaml` (Mailpit) | FR-021 says no email may carry a secret and FR-025 says local development must inspect these emails with no external account. Reading a received message is the only way to check its contents | A stubbed transport asserts on what the sender believed it sent, which is not the requirement. A real SMTP credential in a tutorial repository is worse than an extra container |
| `nodemailer`, first new runtime dependency since 3.4 | SMTP by hand is not this chapter's subject and getting it wrong is invisible until an email is silently malformed | Hand-rolled SMTP adds a protocol implementation to a chapter about limits |
| `ioredis` added to the api | The counters live in Redis and the api is where REST requests arrive | Proxying counter operations through the gateway would couple two services for no reason and put the api's rate limiting behind the gateway's availability |
| Two limiter call sites rather than one | R2: the tenant limiter needs the principal and the auth limiter must work when there is none. The chain positions are forced | One middleware doing both would have to run before authentication and then guess the tenant, which is the header a caller could forge — the mistake chapter 3.2 removed |
| ~35 fences against a 2,000–4,000 word bound, 28 of them before the transport | The scope carries two mechanisms by decision | Recorded in research R10 with a recommendation to split, and the phase order keeps the split available rather than settling it now |
