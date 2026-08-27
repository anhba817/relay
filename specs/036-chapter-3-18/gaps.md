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

    <T031 FR-RTM-10's window, if either path misses it>
    <T038 the gateway's listener-less fan-out client, if the process dies>
    <anything else the work surfaces>
