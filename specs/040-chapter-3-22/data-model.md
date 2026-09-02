# Chapter 3.22 — data model

**Nothing is persisted.** No table, no migration, no ClickHouse write. The whole
model is five Redis keys per user per environment, and the choice of five keys over
one sorted set is argued in `research.md` R3 against a published SAD row.

---

## The slot key

    conn:{environment_id}:{user_external_id}:{slot}      slot in 0..4

| | |
|---|---|
| value | the connection's `id` — `Connection.id`, already `readonly` at `registry.ts:18` |
| TTL | 60,000 ms, the figure `docs/05-sad.md:574` already publishes for this key |
| written by | the gateway instance holding the connection, and only that instance |
| claimed with | `SET key id NX PX 60000` |
| renewed with | `SET key id IFEQ id PX 60000`, every 20,000 ms |
| released with | `SET key - IFEQ id PX 1` on a clean close, and on this instance's shutdown (FR-011a) — **conditional, never a plain `DEL`** |
| released without anybody acting | its own TTL, which is what makes expiry per member |

**Why the value is the connection id and not the instance id.** `docs/05-sad.md:167`
says instance ID, and that is the wrong grain: two connections of one user on one
instance would write the same value to two slots, and neither could tell which slot
was its own to refresh or release. A connection id is unique per connection for its
lifetime, which is what FR-011 requires — *"a connection MUST occupy exactly one
place in the registry for its lifetime"*. This is one of the two things the SAD says
about this key that this chapter has to correct.

**Why `IFEQ` on the renewal, and why `XX` is not enough.** The renewal must extend
the slot **only while the slot is still this connection's**. `SET … XX` tests that
the key exists and nothing more, which the lane's Redis 8.10.0 demonstrates:

    SET k A EX 30        ->  OK    k = A
    SET k B XX PX 60000  ->  OK    k = B     a value it did not own, overwritten

So a connection whose slot expired during a Redis outage longer than the bound comes
back, finds the slot re-claimed by another connection, and its renewal **takes it**.
Both then refresh one key: six connections, five slots, FR-001 and FR-011 violated.
`IFEQ` compares before writing and is refused in both of the cases that matter:

    SET k C IFEQ B PX 60000      ->  OK    right owner, renewed
    SET k D IFEQ WRONG PX 60000  ->  nil   wrong owner, refused
    SET k A IFEQ A PX 60000      ->  nil   key absent, refused

The second and third are the two arms FR-011 needs, and the third is how a connection
learns it has lost its place.

**`presence.ts:195` was cited for this and the analogy does not hold.** That call
refreshes a key whose value is the literal `"1"` — **its value carries no identity, so
ownership cannot be stolen there.** This key's value carries identity. The pattern was
copied without checking whether the property that made it safe came with it.

**Why the release is conditional too, and why this was nearly missed.** `DEL` has no
ownership check any more than `XX` does. A connection whose slot expired during an
outage, was re-claimed by another connection, and then closes cleanly would delete
**the new owner's key** — freeing a slot that is in use. The renewal was fixed first
and the release was left as `DEL`; the defect was found by asking what that fix made
worse.

    SET k x IFEQ OWNER PX 1  ->  OK    and EXISTS is 0 a moment later
    SET k x IFEQ WRONG PX 1  ->  nil   value untouched
    GETDEL                        exists, and is unconditional — no use here

So a release writes a one-millisecond tombstone, only if the slot is still this
connection's. **The millisecond has a consequence and it is the safe direction**: a
claim arriving inside it finds the key present, its `SET NX` fails, and it walks to
the next slot. One slot briefly skipped, never an over-admit. A plain `DEL` fails the
other way.

**Why the slot number is in the key and not in the value.** It is what makes the
claim atomic in one command. `SET NX` on `…:0` either succeeds or does not; two
racers cannot both win it; the loser tries `…:1`. FR-013 is then enforced by Redis
rather than by application logic, which is the difference between a race that cannot
happen and a race that a test hopes to catch.

### State transitions

    (no key)  --SET NX-->  held  --SET IFEQ every 20s-->  held
                             |
                             +--SET - IFEQ id PX 1 (clean close)----> (no key)
                             |
                             +--the same, for every slot this instance
                             |  holds (shutdown)---------------------> (no key)
                             |                                         FR-011a
                             +--TTL expires (crash)------------------> (no key)
                             |
                             +--SET IFEQ refused (renewal OR release)-> lost, and
                                                                        the
                                                                        connection
                                                                        is told

Every transition out of `held` that this code performs is conditional on still owning
the slot. **The only unconditional one is the TTL**, which is the point of the
design.

**A renewal that is refused is a state, not an error, and FR-011b says what follows.**
The connection has lost its place, and it **tries once to claim another**: a free slot
means the outage cost nothing and it carries on with a new slot number; every slot
held by another connection means the cap is genuinely exceeded and this connection is
closed with the refusal a sixth connection gets; an unreachable registry means FR-016
applies and the connection is kept with the cap logged as unenforced. **What it must
never do is carry on as though it still held a slot** — that is six connections
against a count of five. There is no cleanup
path and no prune step, and **the absence of a prune step is the design**: the sorted-set version needs application code to run
`ZREMRANGEBYSCORE` on every read, and code that must run is code that can fail to
run.

---

## Derived, not stored

| quantity | how it is obtained | who needs it |
|---|---|---|
| slots held by a user | 5 minus the free slots found during the claim walk | FR-015's log line |
| whether the cap is enforceable | whether the Redis call answered at all | FR-016, FR-016a |
| which slot this connection holds | held in memory by the connection that claimed it | the renewal, the clean close, and the shutdown release — all three name the slot AND compare the id |
| every slot this instance holds | the instance's own connections, from the local registry | `releaseAll()` on shutdown (FR-011a) |

**The count is discovered, not read, and that is the design's stated cost.** A
sorted set answers "how many" with one `ZCARD`; five keys answer it only by walking
them. FR-015 wants the observed count in the refusal log, and the walk that refuses
has already visited all five, so the number is free *at the point where it is
needed* and expensive anywhere else. Research R3 records the reversal condition: a
future chapter that needs the count without claiming a slot — an admin API, a
dashboard — is the trigger to revisit.

---

## Existing entities this touches

| entity | where | what changes |
|---|---|---|
| `Connection` | `services/gateway/src/registry.ts:17` | nothing. `id` and `identity` are already what the registry needs |
| `ConnectionRegistry` | same file | nothing. `connectionsFor(user)` stays a **local** answer and is never treated as the count (FR-016b) |
| `Identity` | `@relay/protocol` | nothing. Carries `environmentId` and the user's external id, both already resolved at the upgrade seam before `handleUpgrade` |
| `CLOSE_CODES` | `packages/protocol/src/codes.ts` | one entry added; `codes.test.ts` names the set in **two** places — the title at line 18 and the assertion at line 20 — and both go from five to six |
| `ERROR_CODES` | same file | one entry added |

---

## What is deliberately not modelled

- **A registry of instances.** `docs/05-sad.md:167` describes the value as an
  instance ID and nothing needs one. An instance that dies is not looked up; its
  keys expire. Modelling instances would create a second thing to keep true.
- **A count key.** An `INCR`/`DECR` counter cannot expire per member, so one crashed
  instance leaks a slot for ever — the original defect wearing a different shape.
- **Anything about which device holds which slot.** Slot 0 is not "the laptop". Slot
  numbers are allocation detail and no requirement exposes them; the refusal says
  how many are held, not which.








