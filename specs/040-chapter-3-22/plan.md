# Implementation Plan: Chapter 3.22 — the five-connection cap

**Branch**: `040-chapter-3-22` | **Date**: 2026-09-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/040-chapter-3-22/spec.md`

## Summary

FR-RTM-09 permits a user five concurrent connections and nothing counts them. This
chapter counts them, refuses the sixth, and makes the count survive the instance it
was taken on.

Three of the chapter's four design decisions turned out to be governed by rules
already written in the tree, and finding them was cheaper than deriving them. The
fourth contradicts a published document and needs an ADR.

| decision | settled by | where |
|---|---|---|
| refuse after the handshake, with a close code | *"two refusals, two shapes, each because of what it has to carry"* — and FR-004 removes HTTP's only advantage | `session.ts:641` |
| a sixth close code, not a reuse | *"a client that cannot tell them apart retries the wrong one for ever"* | `codes.ts:10` |
| bound 60,000 ms, heartbeat 20,000 ms | three renewals per window; a TTL equal to its refresh expires a live user | `presence.ts:41` |
| **five slot keys, not the SAD's sorted set** | Constitution VII blocks Lua without profiling evidence this chapter cannot produce | `research.md` R3 |
| the renewal is `SET … IFEQ`, not `XX` | measured: `SET k B XX` overwrites a key holding `A`, so `XX` would let a returning connection steal a re-claimed slot | `research.md` R3 |
| the instance releases its slots on shutdown | nothing closes established sockets on a deploy and no 4009 path exists, so a 60 s bound breaks NFR-REL-03 | `research.md` R11a |
| a refused renewal re-claims once, then closes only if the cap is really full | otherwise the mechanism enforcing the cap leaves it exceeded — six open connections against a count of five, with no test looking from the connection's side | `research.md` R11c |
| the release is conditional, not a `DEL` | `DEL` has no ownership check, so a returning connection would free a slot somebody else now holds — the defect the `IFEQ` renewal fix introduced | `research.md` R3 |
| the new fixture takes a per-run environment | it is the only fixture that enforces the cap and it fills all five slots; a constant identity leaks one test's slots into the next | `research.md` R11b |
| `connections` is an optional module, like the other five | required would break three fixtures, two of them fenced, for a cap they do not test — and the whole weight then falls on `main.ts`'s two tasks and the outsider test, which is the bet chapter 3.21 lost and this chapter names | `research.md` R11b |

The last one is a contradiction of `docs/05-sad.md:574` and is treated as one: an
ADR with drivers, rejected alternatives and a reversal condition, plus the SAD
amendment FR-017 already requires because that file **describes this key twice, in
two shapes and two tenses**.

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22, ESM throughout

**Primary Dependencies**: `ws` (the gateway owns its upgrade handler with
`noServer: true`), `ioredis`, `zod` via `@relay/protocol`, `vitest`. No new
dependency.

**Storage**: Redis only. Five keys per user per environment,
`conn:{env}:{user}:{slot}` for slot 0–4, value the connection's id, each with its
own 60,000 ms TTL. Claimed with `SET … NX PX`, **renewed and released with
`SET … IFEQ …`** so neither can touch a slot another connection now holds — the
release is a one-millisecond tombstone, not a `DEL`, because `DEL` has no ownership
check. Released on a clean close and on this instance's shutdown. **A refused renewal
re-claims once** and then either carries on, closes, or keeps the connection with the
cap unenforced, depending on why (FR-011b). **Nothing is persisted** — no table, no
migration, and the same argument FR-RTM-08 made for typing one chapter ago.

**Testing**: `vitest`. Unit tests beside the module for the arithmetic and the
slot walk; one new integration file for the cross-instance behaviour, booting
gateways in process on `server.listen(0)` with a stubbed `ApiClient`, as
`resume.itest.ts` and chapter 3.21's `typing.itest.ts` do. **No api is spawned, so
the lane's spawn count stays at seven.**

**And it is the only fixture that will enforce the cap.** Every gateway module is an
optional parameter — `fanout?`, `limits?`, `presence?`, `membership?`, `typing?` — and
all three in-process files call `attachSessions` with their own module list, so a
fixture that does not pass `connections` claims no slots (`research.md` R11b). The new
file still takes a **per-run environment** and deletes its own keys in teardown,
because it deliberately fills all five slots and a constant identity would leak one of
its tests into the next.

**Target Platform**: Linux, the same three-service compose stack.

**Project Type**: Multi-service TypeScript monorepo — `relay-platform` (pnpm
workspace) with the tutorial in `relay-tutorial`.

**Performance Goals**: NFR-PRF-04, handshake to `connection.ack` p95 < 1 s. The cap
adds one to five local Redis round trips on connect, one more per renewal, and up to
five on a refused renewal that re-claims (FR-011b). **NFR-PRF-04 is not a constraint
that discriminates between the designs** and research R3 records that the round-trip
argument was reached for first and does not hold.

**The periodic cost is the larger one and the first version of this field omitted
it.** The renewal runs every 20,000 ms **per connection**, where presence's refresh
runs every 10,000 ms **per user** — `presence.ts:184` holds a `Map` keyed by user and
`:193` iterates it. At NFR-SCL-01's ten thousand connections and two thousand users:

    presence   2,000 users / 10 s   =  200 SET/s per instance
    the cap   10,000 conns / 20 s   =  500 SET/s per instance   2.5x the rate,
                                                                5x the keys

Nothing threatens NFR-PRF-04, which budgets the handshake only. **But this is the
chapter's first ongoing cost** — claim and release are per-connection events, the
renewal is periodic — and R12 already records that scale is what this lane cannot
measure. These two figures belong beside that admission rather than in nobody's
head.

**Constraints**: CON-02 — WebSocket connections must not require sticky routing for
correctness, which is FR-006 restated as a constitutional clause. NFR-MNT-02 —
100% branch coverage for ordering, idempotency and tenant isolation; the coverage
ratchet pins the new file at 100/100/100/100 by this project's practice rather than
by the clause.

**Scale/Scope**: NFR-SCL-01's 10,000 connections per instance is 2,000 users at five
each, so up to 10,000 slot keys per environment. Trivial by inspection and
**unmeasurable on this lane**, whose largest fixture holds five channels.
NFR-SCL-01 is verified by analysis and stays undischarged.

## Constitution Check

| principle | verdict |
|---|---|
| **I. Tenant isolation** | The key carries the environment: `conn:{env}:{user}:{slot}`. Two environments cannot share a slot for the same user identifier, and FR-012 has a test. The cross-tenant suite attacks endpoints; this adds no endpoint. |
| **II. No acknowledged message lost** | Untouched. A refused connection acknowledges nothing, and FR-005 forbids disturbing an established one. |
| **III. Two data paths** | Untouched. No analytical write, no ClickHouse. |
| **IV. Single writer** | **Passed, and not vacuously.** Chapter 3.21 recorded that Constitution IV can pass for the wrong reason. Here the reasoning is explicit: the registry is ephemeral connection state, the api is the single writer of *persisted* state, and no row is written anywhere. The gateway reaches Redis directly, as presence and typing do. |
| **V. API-first** | No public surface changes. The close code and error code are protocol vocabulary, registered in `@relay/protocol` where a client can read them, and the error reference gains a section — which is the developer-facing half. |
| **VI. Requirement-driven, test-verified** | 21 requirements, each traced. Coverage pinned at 100 on the new file, arms listed before they are written (research R10). |
| **VII. Boring by design** | **This is the principle the chapter argues with.** The clause requiring "a superseding ADR with profiling evidence" for a second language is what rejects the Lua script, and the ADR the chapter owes for contradicting the SAD is required by this same principle. Disagreement attacks the driver: the driver here is that an unmeasurable design decision should not be taken, and this chapter cannot measure. |
| **CON-02, no sticky routing** | The whole point of FR-006. Two in-process instances, three slots on one and two on the other, and the sixth refused on either. |

No violation requiring justification. One deliberate divergence from a published
document, handled by ADR rather than by silence.

## Project Structure

### Documentation (this feature)

```
specs/040-chapter-3-22/
├── spec.md
├── plan.md              this file
├── research.md          R1-R12
├── data-model.md
├── quickstart.md
├── contracts/
│   └── refusal.md       the close code, the error frame, and what a client does
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```
relay-platform/
├── packages/protocol/src/
│   ├── codes.ts                 + one close code, + one error code
│   └── codes.test.ts            the pinned set 5 -> 6
├── services/gateway/src/
│   ├── connections.ts           NEW production file. the slot registry, its own
│   │                            ioredis client — T087 pins its coverage
│   ├── connections.test.ts      NEW test file. the walk, the arms, the intervals
│   ├── connections.itest.ts     NEW test file. two in-process instances, no api
│   │                            spawn — these two are traced by T090, not three
│   ├── session.ts               the cap check in the upgrade path, the renewal,
│   │                            the re-claim branch, and releaseAll() on close
│   ├── session.itest.ts         T011's deliberately red test: six accepted today
│   ├── presence.itest.ts        T047, a comment only — and the file is fenced
│   ├── main.test.ts             the shutdown module set (T042b); the frame count
│   │                            at line 43 stays 11 (T023a)
│   └── limits.itest.ts          the port map: two missing ranges and the overlap
├── services/gateway/src/main.ts TWO edits: the attachSessions argument AND
│                                 registering close() in shutdown() (see below)
├── vitest.coverage.config.mts   the 100/100/100/100 pin — and the ONLY file this
│                                 chapter touches that the appendix amends
└── packages/outsider/src/
    └── integrate.itest.ts       the sealed client holds five and is refused a sixth

docs/
├── 04-srs.md                    FR-RTM-09 marked built; EIR-WS-06's classes
├── 05-sad.md                    the conn: rows RECONCILED, both of them
├── 06-adr-deep-dives.md         ADR-23
├── 07-tutorial-plan.md          the chapter row, which stops at 3.21 without it
└── 08-error-reference.md        the new close code and error code

relay-tutorial/
├── app/(en|vi)/…/chapter-22/    the page and four figures, both locales
├── lib/tutorial.ts              status: published, translatedIn: ["vi"] — the
│                                 sitemap derives from this and needs no edit
└── fences/post-series.md        the appendix hunk for the coverage config
```

**Six of those were missing until analysis pass 11.** `session.itest.ts`,
`presence.itest.ts` and `vitest.coverage.config.mts` were absent from the day this
block was written; `main.test.ts`, `docs/07-tutorial-plan.md` and `lib/tutorial.ts`
were added to the task list by passes 6, 7 and 8 and this block did not follow.
**Three passes have now found the same drift in a different descriptive section** —
the checklist (pass 7), the spec's assumptions (pass 10), and this.

**Structure Decision**: One new gateway module with its own Redis client, following
`presence.ts` (chapter 3.19) and `typing.ts` (chapter 3.21). No new service —
Constitution VII's "deliberately not a separate service" table applies: same
datastore, same transactions, same team.

**`main.ts` needs TWO edits, the module is optional, and those two facts are the same
fact.** Optional is what let chapter 3.21's module go unpassed and still compile.

**`main.ts` needs TWO edits and doing only one of them is how chapter 3.21 failed.**
That chapter built its module, awaited its `close()` in `shutdown()` — **so lint saw
a used variable** — and never passed it to `attachSessions`. The feature was inert
while 1,174 coverage tests and 174 gateway integration tests were green, and
`**/main.ts` is excluded from coverage so no number could have shown it. `main.ts:99`
records that sequence in its own comment.

So this chapter's two edits are named separately and neither is allowed to stand in
for the other: **the `attachSessions` argument**, without which the cap does nothing,
and **`connections.close()` in `shutdown()`**, without which every gateway leaks a
Redis client. The outsider test is what proves the first, and it is a requirement of
the plan rather than a polish item.

## Phases

**Phase 1 — premises.** Re-run every command in `research.md` and `quickstart.md`
before building on any of them. Chapter 3.21 had three wrong task premises that
survived to Phase 1 and one wrong published claim that survived twelve analysis
passes; the cheapest place to find them is here. Specifically: the presence/meter
port overlap (R7), the `policy.ts` arithmetic (R6), and that `grep` for `.eval(`,
`defineCommand` and `.multi(` still returns nothing (R3, the whole basis for
rejecting Lua).

**Phase 2 — US3, on unchanged code.** FR-014's tests, written before any production
change so they are a regression guard for the cap rather than a description of it.
**This was Phase 6 in the first draft of this plan and `tasks.md` moved it**: US3
tests behaviour that already ships (research R5), and a characterisation test written
after the change proves nothing — nobody would know it had ever passed. Each test is
falsified first by breaking the delivery site it covers.

**Phase 3 — the protocol.** The sixth close code and the error code, with **both**
places in `codes.test.ts` that name the set updated from five to six — the assertion
and the test's own title. Before the module because everything imports it, and
because `check:errors` reads `packages/protocol/dist/codes.js` — the **built**
artifact — so a stale `dist` makes that gate green for the wrong reason.

**Phase 4 — the registry module.** `connections.ts` and its unit tests, including
`releaseAll()` and the **re-claim on a refused renewal** (FR-011b, R11c) — the branch
that decides whether a brief Redis outage costs a user their connection or nothing at
all. The arms listed before they are written (R10). Tested against a real
Redis, because **`SET NX` and `SET IFEQ` semantics are the entire correctness
argument** and a stubbed client would pass with a non-atomic implementation — and
with an `XX` renewal that silently hijacks, which is the defect R3 records against
its own first draft.

**Phase 5 — US1, the seam.** 🎯 MVP. The cap check in `session.ts`'s upgrade path after
`authenticate` and after the rate limiter, the heartbeat timer, the clean-close
`DEL`, and `main.ts`. Ends with the outsider test, not with a unit test.

**Phase 6 — US2, cross-instance.** **One module per gateway instance, created inside
the fixture's `boot()`** as `typing.itest.ts:101` does — `releaseAll()` releases the
slots *this instance* holds, so a shared module would have a destroyed instance
release the survivor's slots and the crash test would pass for the wrong reason.
`connections.itest.ts`: two gateways in process, the
count spanning both, an instance dying without closing its sockets, and the slot
still held at 59 s. Plus the FR-013 race, whose test is written only after the
falsification in R11 has been run.

**Phase 7 — the race.** FR-013, and only after R11's falsification has been run:
if removing `SET NX` turns nothing red, the ordering is unobservable and the test
asserts the invariant instead.

**Phase 8 — failing open.** FR-016, where the log line is the only evidence (R9).

**Phase 9 — documents.** ADR-23, the two reconciled SAD rows, the SRS, the error
reference, and the port map's two comment lines.

**Phase 10 — the tutorial.** The chapter page in both locales, the fences, the
figures.

**Phase 11 — close-out.** Gates, coverage, the battery, `gaps.md`, `chapter-notes.md`,
`baseline.txt`, traceability, the tag.

**Eleven phases, and `tasks.md` is the authority on their order.** This section was
written with nine and with US3 last; the task breakdown moved US3 to second and split
the race and the fail-open path into phases of their own. **The plan is edited to
agree rather than left to be overridden** — two documents disagreeing about the phase
order is what this chapter's `sweep.py` compares, and chapter 3.21 recorded the phase
order in `baseline.txt` and applied it only to `tasks.md`.

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed
work twice in chapter 3.12.

## Complexity Tracking

| what | why it is not simpler |
|---|---|
| Five keys instead of one sorted set | The one-key version needs Lua for FR-013's atomicity, and Constitution VII requires profiling evidence for a second language that this lane cannot produce. Stated with its cost: no cheap count, 1–5 round trips. |
| A renewal flag most readers will not know | `SET … IFEQ` is newer than the rest of this codebase's Redis usage and appears nowhere else in it. It is still the simplest correct answer: the alternative that avoids it is a compare-then-set, which is two commands and a race. Measured available on Redis 8.10.0 and typed in ioredis 6.0.0, so it costs a comment rather than a dependency. |
| A release path on shutdown | Without it a deploy holds five slots for a full bound and breaks NFR-REL-03 on the ordinary path, not an unlucky one. `wss.close()` does not close established sockets and there is no 4009 drain (R11a). |
| A sixth close code | `codes.test.ts` pins the set, so it is a decision either way. Every reuse fails the "retries the wrong one for ever" test — the table is in research R2. |
| A third timer in the gateway | `PING_INTERVAL_MS`, presence's refresh, and now the slot heartbeat. Chapter 3.19's rule says these are separate quantities and tying them is the bug; the tests assert the ratio, not the values. |
| A tenth gateway integration file | Chapter 3.21 established the real constraint is api **spawns**, not files: seven of ten spawn, and this one does not. The spawn count stays at seven. |

## Deliberately out of the plan

- Changing `connect: 3_000`. Research R6 states the arithmetic and hands it to
  `gaps.md`; re-tuning another chapter's shipped limit in the same battery as a new
  cap would make two changes indistinguishable.
- Making the cap configurable. FR-RTM-09 states one number.
- Fixing the five files that discard their children's output (chapter 3.21's
  ninth gaps item). It is addressed to this chapter and it is a close-out decision,
  not a design one — recorded in Phase 11's task list (T092), not in the design.
