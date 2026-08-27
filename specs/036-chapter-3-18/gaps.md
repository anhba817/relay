# Gaps — chapter 3.18

*One item per gap, each with an owner. Written when found, not at close-out.*

## 1. The two entrances accept different idempotency keys — FOUND IN T003

    REST body    idempotency_key: z.string().uuid()           messages.schema.ts:13
    socket frame idem_key:        z.string().min(1).max(255)  frames.ts

A client that retries the same logical send over both doors cannot use one key. Neither
contract is wrong on its own and nothing in the SRS requires them to agree, but FR-MSG-04's
24-hour dedup is one property described by two grammars. This chapter mirrors the gateway's
retry guard into the api (FR-006, FR-007) and so is the first thing to depend on both.

**Owner:** unassigned. Not this chapter's to fix — it predates it and closing it means
changing a public route's contract. Recorded so the next chapter that touches idempotency
does not rediscover it.

## 2. A fourth file permanently outside the fence chain — DECIDED IN T014a

`services/gateway/src/session.itest.ts` is fenced by no chapter and chapter 3.18 leaves it
that way, showing its new delivery block as an `(excerpt)`. It joins `sentinel.ts`,
`sentinel.sql` and `guard.itest.ts` in chapter 3.17's item 7.

The consequence is specific: **the end-to-end test that proves this chapter's claim — a
REST send reaching a real socket — is never replayed against the repository.** The
alternatives were worse (a 582-line titled fence, or a second file duplicating a harness
that spawns the api), and `chapter-notes.md` records why.

**Owner:** unassigned. The general fix is a fenceable shared test harness, which is a
feature of its own and not this chapter's.

## 3. The integration lane is not idempotent from cold volumes — FOUND IN PHASE 2

The first `pnpm test:integration` after `docker compose down -v` fails; the second passes.
Measured: all 16 dispatcher tests red on the first run and green on the second, and green
when the dispatcher package is run alone. `ensureStream`
(`services/api/src/outbox/jetstream.publisher.ts:84`) is reached from
`consumer/runtime.ts`, which the lane disables with `RELAY_EVENT_CONSUMER=off`, so no step
creates JetStream state on purpose — the first run creates it as a side effect and later
packages in the same run depend on it.

CI does not see this: its runner has no volumes and its first run is the run.

**Owner:** unassigned. The fix is a bootstrap step that calls `ensureStream` before the
lane, which is a small script and somebody's chapter. Until then: run it twice after a
`down -v` and believe the second.

## 4. FR-RTM-10's five-second window is not met, on either path — MEASURED IN T031-T034

**FR-RTM-10 (P1):** events *"shall not be delivered to a client whose membership no longer
grants access, effective within 5 seconds of the membership change."*

Measured: a member removed over `POST /v1/channels/:id/members/remove` keeps receiving on
an open socket **indefinitely**. The test is
`services/gateway/src/session.itest.ts` — *"keeps delivering to a member who was REMOVED
while connected (FR-RTM-10)"* — and it asserts the violation, waiting 5,500 ms first so the
clause's own budget is spent before the assertion.

**The mechanism, read before the test rather than after it:**

    session.ts:355   registry.add(connection)          channelIds is a Set built ONCE, at
                                                       connect, from POST /internal/session
    session.ts:356   fanout.subscribe(...)             run once over that set
    session.ts:175   registry.subscribersOf(channelId) the delivery lookup, reading the
                                                       same set on every frame
    session.ts:398   fanout.unsubscribe(...)           run once, when the socket CLOSES

Nothing between connect and close re-reads membership. There is no path that could: the
gateway has no database (ADR-05) and learns memberships only in the session response.

**THIS IS NOT CHAPTER 3.18's REGRESSION.** The gap has existed for socket-originated
messages since chapter 2.6; this chapter gives it a second entrance. FR-013 was written to
forbid assuming the socket path's answer covers the REST path — the answer turns out to be
the same on both, and it is "no".

**FR-013 was NOT narrowed to make a test pass.** T034 said not to and the temptation was
real: the clause could have been read as "within 5 seconds of a *reconnect*" and everything
would be green. That reading is not what it says.

**Owner:** chapter 3.19. Presence needs the same missing mechanism — something that tells a
gateway a membership changed — and FR-RTM-06's grace period is the same shape of problem.
Whoever builds that closes this. The test above inverts on that day.

## 5. Two comments state that a missing ioredis error listener kills the process — MEASURED IN T041

    services/api/src/limits/store.ts:137   "Without a listener ioredis emits `error` on an
                                           EventEmitter with none attached, which Node turns
                                           into an unhandled exception and the api dies"

Measured against ioredis 6.0.0 by reproducing `createFanout`'s exact client: the process
**stays alive**. ioredis prints `[ioredis] Unhandled error event: …` itself and continues.
Seven lines in four seconds against a dead port.

The listener is still worth attaching — those lines are unstructured, unbounded, and
defeat NFR-OBS-01 — but the stated reason is wrong, and `services/gateway/src/fanout.ts`
is not the hazard R10 supposed. Chapter 3.18's own publisher attaches one for the accurate
reason, which is in its comment.

**Owner:** unassigned. Correcting `limits/store.ts`'s comment means editing a file chapter
3.8 fences, for a claim that chapter made; a later chapter touching the limiter should fix
it there rather than this one reaching across.
## 5. Two comments state that a missing ioredis error listener kills the process — MEASURED IN T041

    services/api/src/limits/store.ts:137   "Without a listener ioredis emits `error` on an
                                           EventEmitter with none attached, which Node turns
                                           into an unhandled exception and the api dies"

Measured against ioredis 6.0.0 by reproducing `createFanout`'s exact client: the process
**stays alive**. ioredis prints `[ioredis] Unhandled error event: …` itself and continues.
Seven lines in four seconds against a dead port.

The listener is still worth attaching — those lines are unstructured, unbounded, and
defeat NFR-OBS-01 — but the stated reason is wrong, and `services/gateway/src/fanout.ts`
is not the hazard R10 supposed. Chapter 3.18's own publisher attaches one for the accurate
reason, which is in its comment.

**Owner:** unassigned. Correcting `limits/store.ts`'s comment means editing a file chapter
3.8 fences, for a claim that chapter made; a later chapter touching the limiter should fix
it there rather than this one reaching across.
    <anything else the work surfaces>
