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

    <T031 FR-RTM-10's window, if either path misses it>
    <T038 the gateway's listener-less fan-out client, if the process dies>
    <anything else the work surfaces>
