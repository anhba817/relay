# Research — chapter 3.19, presence

*Every entry is a question with a yes-or-no or a number for an answer. Where a
command was run, its output is here rather than its conclusion.*

**Line numbers in this file describe the tree at the fence predecessor `caeabc9`**, and they are evidence about what the code says today, not navigation targets. This feature edits `services/gateway/src/session.ts` five times, so every number below line 100 in that file moves during implementation. Tasks anchor on symbols for exactly that reason.

---

## R1 — Can a second frame kind travel the existing fan-out subject?

**No, not without changing the message path's parse.** Read, not assumed — and the paths are
written out because the protocol package holds a `fanout.ts` too, which this feature leaves alone:

    services/gateway/src/fanout.ts:47   publish(message: Message): Promise<void>
    services/gateway/src/fanout.ts:80   messageCreatedSchema.shape.payload.safeParse(parsed)
    services/gateway/src/fanout.ts:82   logger.log("error", "fanout.invalid_payload", …)
    services/gateway/src/session.ts:194 send(socket, { type: "message.created", payload: message })

Three points hardcode the kind, and the third is inside a function fenced by ten
chapters. A presence payload published on `chan:{id}` today produces
`fanout.invalid_payload` and no frame.

**Decision: a second subject grammar — `presence:{channel_id}` — in a new module
that owns its own Redis clients.** `packages/protocol/src/fanout.ts` gains a
`subjectForPresence` beside `subjectForChannel`; `services/gateway/src/presence.ts`
is new; `fanout.ts` is not touched at all.

> **Superseded during planning.** Putting `subjectForPresence` in `fanout.ts` costs a
> `diff` hunk on a file chapter 3.18 fences, and the second sentence here already says
> `fanout.ts` is untouched — the two halves of this decision contradicted each other.
> `packages/protocol/src/presence.ts` is new too. See `plan.md`, Structure Decision.

**Rationale.** The message path is the highest-volume path in the system and it
would gain a discriminated-union parse to serve the lowest-volume one. Separating
the subjects also makes cross-kind mis-delivery structurally impossible instead of
test-enforced: a presence payload cannot arrive where a message parse is waiting,
because nothing publishes it there. And `fanout.ts` stays byte-identical, which
keeps two chapters' hunks (2.6, 3.18) off the table.

**Alternatives considered.**

- *Envelope both kinds on `chan:{id}`.* Fewer subscriptions — one per channel
  rather than two — and it reads closer to ADR-10's wording. Rejected on the two
  costs above. The subscription count is the honest price of this decision and
  T0-phase should measure it: a user in 20 channels issues 40 `SUBSCRIBE`s at
  connect instead of 20. ioredis accepts a variadic `subscribe(...)`, so it is one
  round trip either way.
- *Pattern subscribe (`PSUBSCRIBE`).* Redis pattern matching runs per published
  message against every pattern; it is the one option that gets worse with scale.

**Consequence for FR-017:** ADR-10 says transitions publish "on the affected
channels' subjects only". Under this decision that sentence stays true in spirit
and false in letter — the subject is *derived from* the affected channel, not the
channel's own. The SAD amendment says so.

**And the architecture already named this remedy.** ADR-10's deep dive
(`docs/06-adr-deep-dives.md:651`) says that when presence exceeds ~30% of gateway
publish volume, *"presence subjects get their own fabric or channels opt in, per Open
Question 3."* **This chapter takes the first of those two remedies before the trigger
fired**, for a reason the trigger does not mention: the fan-out is typed to messages at
three points, so the alternative is not "keep it simple", it is "edit the hot path".

That is worth saying out loud rather than quietly benefiting from, because a later reader
who finds presence on its own subject will reasonably conclude the 30% trigger fired. It
did not, and nothing here measured it — see FR-016a. The deep dive was found by running the task list's own
`grep` for open question 3 across `docs/` while writing that task; reading alone had not opened
that file.

---

## R2 — A TTL expiring publishes nothing. Who publishes `offline`?

The clause needs an event 30 seconds after the last connection closes. Redis
deletes a key silently; no gateway is told.

**Decision: the instance whose last local connection for that user closed schedules
one check at `+graceMs`, and publishes `offline` only if the presence key is absent
at that moment.** Election between instances is a `SET … NX`.

**Rationale, and the arithmetic that makes it correct.** The presence key's TTL,
refreshed while any instance holds a connection, *is* the cross-instance liveness
signal. At the check, "key absent" means no instance refreshed it for a full TTL,
which means no instance holds a connection. Nothing else has to be asked, and
`docs/05-sad.md:574`'s `conn:{env}:{user}` set is not needed — see R6.

Two instances closing their last connections at different times behave correctly
without coordinating: A closes at t=0 and checks at t=30, B closes at t=5 and checks
at t=35. B's refreshes kept the key alive until t≤35, so A's check at t=30 finds it
present and stays quiet; B's at t=35 finds it gone and publishes. The grace is
measured from the *last* close, which is what FR-RTM-06 says.

Two instances closing at the *same* time both find it absent, and that is the
duplicate FR-012 forbids. Hence the election.

**Measured, against the running Redis 8.10.0:**

    SET k 1 NX EX 3    -> OK          first caller
    SET k 1 NX EX 3    -> (nil)       second caller loses
    SET k 1 XX EX 3    -> OK          refresh while present
    DEL k; SET k XX    -> (nil)       refresh FAILS when absent — a detectable state,
                                      not a silent one

    SET k 1 EX 1; EXISTS k  -> 1
    sleep 2; EXISTS k       -> 0      the TTL alone is the offline signal

**Alternatives considered.**

- *Redis keyspace notifications on expiry.* **Measured off:**
  `CONFIG GET notify-keyspace-events` returns an empty value on the compose Redis.
  Turning it on is a server-config change in `compose.yaml` and an operational
  dependency in production, and it would deliver every expiry to every gateway,
  which then still need an election. Rejected on cost, not on taste.
- *A periodic sweeper scanning for expired presence.* Needs a keyspace scan on a
  timer. Rejected.

---

## R2a — The two clocks, and the defect that came from assuming they were one

**Found in analysis pass 1, after R2 and R3 were written and before any code.** R2's design is
correct and R3's numbers are correct, and put together they were wrong.

The key's expiry and the grace check are driven by different events:

    key expires at   last_refresh + ttlMs      (30 s from whenever the loop last ran)
    grace ends at    close        + graceMs    (30 s from the socket closing)

Those are not the same instant. They differ by `close - last_refresh`, which is uniformly anywhere
in `[0, refreshMs)` — up to ten seconds. So the key dies **before** the grace ends, and in that gap
the state is "no key" while the requirement still says "online".

A reconnection landing there calls `connected`, finds no key, wins `SET … NX`, and publishes a
second `online` for a user who never went offline. FR-007: *"A reconnection inside the grace period
MUST publish nothing — neither an `offline` nor a repeated `online`."*

**The fix is one command at the close, not a change to the numbers:**

    SET presence:{env}:{user} 1 XX PX graceMs

`XX` so it cannot resurrect a key that has already gone. The key then dies exactly when the grace
ends. An instance still holding a connection for that user pushes the TTL back to `ttlMs` on its
next refresh — at most `refreshMs` later, well inside the window — so the multi-instance case is
untouched and the grace stays measured from the last close.

**What makes this worth writing down rather than quietly fixing:** the tests planned for it could
not have caught it. Every reconnect case planned at that point landed at a half or a third of the
grace window, and the gap only opens after `ttlMs` has lapsed — the last third. So every planned
reconnection sat inside the key's life, where `NX` correctly fails and the suite goes green. The
late-reconnect case exists now, and it exists because of this paragraph. The bug and its test
suite were designed by the same reasoning, which is the failure mode CLAUDE.md describes as *tests
that pass while proving nothing*: ask what would have to be false for this to fail.

This rests on the `SET NX`/`XX` and expiry behaviour already measured in R2 plus the arithmetic
above. It was not separately simulated — the compose stack was down by the time it was found.

---

## R2b — The fix for R2a was itself wrong, and the second defect was worse

**Found in analysis pass 2, auditing pass 1's own remediation.** R2a's fix pins the key to `graceMs`
at the close. The check was already scheduled at `graceMs`. Those are the same instant measured by
two clocks:

    key expires at    close + δ + graceMs      δ = the SET's round trip to Redis
    check fires at    close     + graceMs + ε  ε = timer lateness, >= 0, often ~0

`ε < δ` puts the check ahead of the expiry. `EXISTS` returns 1, the branch logs
`presence.suppressed` and stops, and **the timer is one-shot** — its `pending` entry is rewritten
only by the next close. So the `offline` is not delayed, it is never published. FR-004 is a MUST.
Redis also holds a key alive until `now` is strictly past its expiry, so equality falls on the wrong
side too.

**R2a's defect produced a spurious `online`. Its fix produced a user permanently stuck online.** The
repair traded a cosmetic duplicate for a missing state transition — the worse of the two — while
claiming to close a CRITICAL.

**The fix, in two parts, neither sufficient alone:** `await` the re-pin before arming the timer, so δ
sits inside the wait rather than racing it; and arm the timer at `graceMs + marginMs`, with
`marginMs` defaulting to 1 s and overridable, so the tie is broken and timer granularity absorbed.
Publishing later is compliant — FR-004 bounds the delay from below only.

**What this says beyond presence.** A fix for a CRITICAL is new design, and the pass that writes it
is not the pass that can check it. Pass 1 found R2a by asking what the tests could not see; pass 2
found R2b by asking the same question of the answer. Same question, two consecutive passes, two
defects — the second one created by the first one's fix. `ttlMs >= graceMs` also stopped being the
mechanism without the section that named it being retitled, which is how a document goes on
asserting a reason that has moved.

---

## R3 — Which timer refreshes the key, and how do the three 30-second numbers relate?

**They are three different quantities and the repository currently has one number
for all of them.**

    PING_INTERVAL_MS        session.ts:41    30_000    EIR-WS-04's contract
    FR-RTM-06 grace period  docs/04-srs.md:473  30 s   time from last close to offline
    presence key TTL        docs/05-sad.md:575  30 s   liveness window

**A TTL equal to its refresh interval expires while the user is still connected.**
If the presence refresh rode the ping loop, the key would be rewritten every 30 s
with a 30 s TTL, and any scheduling slip past the deadline drops a live user offline.

**Decision: presence gets its own interval, default 10 s, against a 30 s TTL, and `ttlMs >= graceMs`.**
Three refreshes per TTL, so two consecutive misses still do not expire a live user.
`PING_INTERVAL_MS` is not touched — it is a protocol contract, and the meter already
set the precedent of a second timer beside the heartbeat rather than a second job for
it (`session.ts:163`).

The arithmetic the grace check depends on: with the last refresh at most 10 s before
a close and a 30 s TTL, the key expires no later than 20 s after the close and the
check runs at 30 s. It is always gone when nobody is left.

**"And never gone early enough to matter" is what this paragraph said, and it was
wrong.** Nothing *looks* before 30 s, but something *acts* before 30 s — a reconnection.
The ten seconds between the key's death and the grace's end is a window in which a
returning user is treated as a new arrival. R2a has the arithmetic and the fix.

---

## R4 — Are the grace-period tests affordable?

**Not at 30 seconds each.** The lane closed chapter 3.18 at 41 files, 607 tests,
195 s wall against a 240 s budget — **45 s of headroom**
(`specs/036-chapter-3-18/baseline.txt:524-534`). User story 2 alone has five
acceptance scenarios that each wait out a grace period. Six real 30-second waits is
180 s against 45 s.

**Decision: `presenceGraceMs`, `presenceTtlMs` and `presenceRefreshMs` are
`SessionServerOptions` fields with production defaults, overridable in tests** — mapping to
`PresenceOptions`' bare `graceMs`, `ttlMs` and `refreshMs` the way `session.ts:168` already
passes `intervalMs: meterIntervalMs` to `createMeter`.
This is not a new affordance; it is the one `session.ts:126` already documents —
*"Overridable so tests can run the heartbeat in milliseconds instead of half-minutes
— the interval is a contract (EIR-WS-04), not a constant the tests should have to
wait out."* Two more fields follow `pingIntervalMs`, `resumeDeadlineMs` and
`meterIntervalMs`.

**One test must use the real 30 seconds**, or the number in the clause is asserted
nowhere: a single case that reads the production default and checks it equals 30_000.
That costs no wall clock and is the only thing standing between the clause and a
constant somebody edits later.

---

## R5 — How does a watcher avoid receiving one frame per shared channel?

A transition publishes on the presence subject of each of the subject's channels. An
instance subscribed to three of them, hosting one connection that shares all three,
receives three deliveries for one transition. The client frame carries `user` and
`state` and no channel, so the three are indistinguishable duplicates — FR-012.

**Decision: the internal presence payload carries a `transition` id the publisher
mints, and a receiving instance delivers a given transition to a given connection at
most once.** The id never reaches a client: the frame sent on the wire stays exactly
`{ type: "presence.changed", payload: { user, state } }`, which is what chapter 1.3
published and `frames.test.ts` asserts.

**Rationale.** It is exact rather than heuristic. The internal fabric payload and the
public frame become two different shapes for the first time — the message path never
needed the distinction, because its payload *is* the frame's payload.

**Alternatives considered.**

- *A suppression window per connection, keyed on `(user, state)`.* Simpler and
  needs no payload field. The argument for it is real: the window would be well
  under the grace period, so no legitimate transition pair could fall inside it.
  Rejected because it answers "were these the same transition?" with a clock.
- *Carry the subject's whole channel list in the payload and have each receiver pick
  a canonical shared channel.* Exact, no nonce — but it hands every instance hosting
  one co-member the subject's full channel set, including channels that instance hosts
  nobody for. A widening of what a gateway knows, for no gain over a nonce.

---

## R6 — Does this chapter need `conn:{env}:{user}`?

**No — and the shape the SAD specifies for it does not work.**
`docs/05-sad.md:574` names `conn:{env}:{user}` → set of instance IDs, *"60 s,
heartbeat-refreshed"*. **A Redis TTL is per key, not per set member.** One instance
refreshing the key's TTL keeps a dead instance's member alive forever; there is no
expiry that removes just one entry. A correct version is a sorted set scored by
heartbeat time, pruned with `ZREMRANGEBYSCORE` on read — or the design in R2, which
needs no membership at all because it asks a yes-or-no question rather than a count.

**Decision: not built here.** R2's presence key answers the only question this
chapter asks. Recorded because FR-RTM-09's five-connection cap will need a count,
and it is the clause that cites this key.

---

## R7 — Is FR-RTM-10 in scope? (FR-020a demands a recorded answer)

**No. Recorded on a reason, not on the default.**

My first reason was wrong and is worth writing down because it would have justified
the same answer badly. I argued a membership change cannot reach the gateway holding
the user's connection, because the gateway subscribes only to the channels the user
was in at connect and an *added* channel is not among them. True for adds. **FR-RTM-10
is about removals** — *"a client whose membership no longer grants access"* — and on a
removal the gateway is still subscribed to that channel. A removal notice travels on
the existing subject grammar perfectly well.

So the honest reason is smaller and different: FR-RTM-10 needs a third payload kind,
a publisher on the api side, and a mutation of `connection.channelIds` plus an
`unsubscribe` on a live connection. None of that is machinery presence builds, and
none of it is blocked by presence either. It is a second argument in a chapter that
has one, and prose tracks arguments — 3.17 taught 16 files to make one argument and
came in 45% below the word rate 3.15 and 3.16 agreed on.

**What presence does make cheaper later:** the second-subject grammar and a
non-message payload crossing the fabric. That is a reason to record the finding, not
to bundle the work.

**The distinction FR-021 needs:** the *add* case is the genuinely unreachable one, and
it is exactly presence's own staleness — a user who joins a channel while connected
does not appear online to that channel's members until they reconnect.

---

## R8 — Where do the transitions hook into `session.ts`?

Two points that already exist, both already carrying an ordered comment:

    session.ts:355   registry.add(connection)     ->  presence.connected(...)
    session.ts:391   registry.remove(...)         ->  presence.disconnected(...)

The close handler's order is already documented and load-bearing: the meter is told
*before* `registry.remove` because a socket that opened and closed between two reports
would otherwise be counted zero. Presence must be told **after** `registry.remove`, so
that "is this the last local connection for this user?" is answered by a registry that
no longer contains the closing one. Opposite requirement, same handler, three lines
apart — and it is the kind of ordering a later edit silently breaks, so it wants a
test that fails when the two calls are swapped.

`Registry` has no per-user index; `all()` exists and the per-instance set is small.
A `connectionsFor(user)` helper or a filter over `all()` both work.

---

## R9 — How many Redis connections does a gateway hold after this?

**Five.** Two from `createFanout` (a subscriber cannot issue ordinary commands, so
publisher and subscriber are separate), one from chapter 3.8's limiter, and two more
here — presence needs a subscriber *and* a command client, because `SET`, `EXISTS`
and `PUBLISH` cannot run on a subscribed connection.

**Decision: `presence.ts` owns both of its clients and its own `close()`.** Chapter
3.8 set the precedent and stated the reason at `services/gateway/src/main.ts:40` — *"A SECOND Redis client,
not fanout's — one of fanout's two is a subscriber… and so its close has an owner."*
Reaching into `fanout`'s publisher would save one connection and couple two modules'
lifecycles.

**`error` listeners on both.** Chapter 3.18 measured that the stated reason for these
listeners is wrong — ioredis 6.0.0 prints `[ioredis] Unhandled error event: …` and the
process **stays alive** (chapter 3.18's `gaps.md` item 5) — and the accurate reason still holds: those
lines are unstructured and unbounded and defeat NFR-OBS-01. `createFanout` has no
listener; both rate limiters do. The new module attaches them with the accurate reason
in the comment.

---

## R10 — What must presence delivery NOT do that message delivery does?

`deliver` (session.ts:175-196) consults `connection.phase` and buffers during a resume,
then consults `connection.marks` and suppresses anything at or below what the backfill
already delivered.

**Neither applies to presence, and a separate delivery path is how that stays true.**
Presence carries no sequence, so it cannot duplicate a backfilled row and cannot leave
a gap; buffering it would delay a frame for no benefit, and `suppressed()` takes a
`Message`. A presence frame is sent immediately regardless of `phase`.

The `MAX_BUFFERED_FRAMES` overflow flag and `marks` stay message-only. Worth one test:
a presence transition during a resume arrives, and does not appear in the buffer.

---

## R11 — What happens when Redis fails mid-life?

- **`SET … XX` returns nil** while a connection is still open: the key vanished (a
  Redis restart, an eviction). The instance treats it as a new transition and publishes
  `online` again. A duplicate `online` for a user who never left, which ADR-10 permits —
  presence loss is cosmetic and self-heals — and which is better than a user who is
  online and unpublishable.
- **The instance dies inside the grace window.** Nothing publishes `offline`; the key
  expires silently and watchers hold a stale green circle until the subject next
  transitions. Named in the spec's edge cases; it must be a sentence in the chapter,
  not a discovery.
- **Redis unreachable at connect.** The socket must still open (FR-023) and the failure
  must be one structured log line (FR-024). Chapter 3.18's trap applies exactly: the
  fan-out's `publish` swallows its errors and resolves, so "the socket opened with Redis
  down" is equally true of a presence path that does nothing at all. **The assertion that
  carries FR-023 is the log line, and the test that proves the path is alive is the one
  that restores Redis and sees the next transition published.**

---

## R12 — How is the cross-instance case tested?

`fanout.itest.ts` answers half of it: two `createFanout` clients on one Redis stand in for
two gateway instances — *"same code, same Redis, no knowledge of each other."* Presence
needs the same at the fabric level.

**At the session level it does not exist, and my first draft of this entry said it did.**
Counted rather than remembered:

    attachSessions( calls per gateway itest
    0  fanout.itest.ts     3  isolation.itest.ts   1  limits.itest.ts
    0  meter.itest.ts      1  public-surface.itest.ts   1  resume.itest.ts
    4  session.itest.ts

Every one of them stands up **one** session server inside its own `describe`, with its own
`beforeAll`/`afterAll`. No suite runs two concurrently against one Redis. `session.itest.ts`
also spawns a real gateway from `dist/main.js` (line 159), which is a second, heavier way to
get an instance.

**So the two-instance session harness is new work, not a pattern to copy** — two
`attachSessions` on two ports in one test process, sharing one Redis. It is a task, and it is
the sort of thing that otherwise surfaces mid-implementation as a surprise.

Both files namespace by fresh channel UUIDs per run, for a reason worth repeating:
*"Redis pub/sub has no namespaces, so two suites publishing to a hard-coded subject on
one broker read each other's frames."* The presence key is `presence:{env}:{user}`, so
the same discipline means a fresh user id per run, not just a fresh channel.

---

## R13 — Two files instruct a Redis port that is not listening

`services/gateway/src/fanout.itest.ts:18` and `services/gateway/src/resume.itest.ts:26` both carry:

    //   RELAY_REDIS_PORT=16379 pnpm --filter @relay/gateway test:integration

while the line below defaults to `6379`. **Measured on this machine:**

    16379   connection refused
    6379    open, redis_version:8.10.0

**This is not a wrong port; it is an unconditional instruction for a conditional
situation.** `compose.yaml:37` maps `"${RELAY_REDIS_PORT:-6379}:6379"` and chapter 1.2
documents `RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 docker compose up -d --wait`
as the override for a host that already runs its own. A reader who took chapter 1.2's
plain `docker compose up -d` and then this comment verbatim gets a refused connection.
Seven chapters mention 16379 across both locales, and they are describing the override.

I nearly recorded this as "the published chapters are wrong". They are not, and the
correction belongs here rather than in a finding: the two comments present one valid
invocation as though it were the only one.

**Owner: not this chapter.** Both files are fenced (2.6, 2.7) and the fix is a
conditional clause in a comment. Recorded for `gaps.md`.

---

## R14 — What the environment must be before anything is measured

**Measured now, and it is wrong for a lane run:**

    docker ps  ->  relay-api-1, relay-gateway-1, relay-dispatcher-1  ALL UP

`baseline.txt` requires the compose `services` profile stopped for
`pnpm test:integration` **and** for `pnpm coverage` — the second requirement was added
by chapter 3.18 after a live `relay-dispatcher-1` moved a branch pin on
`services/dispatcher/src/expand.ts` from 92.30% to 84.61% on a byte-identical file, and
half an hour went to proving 3.18 innocent (chapter 3.18's `gaps.md` item 7).

Also inherited: **the lane is not idempotent from cold volumes** (chapter 3.18's `gaps.md` item 3).
After `docker compose down -v`, the first `pnpm test:integration` fails and the second
passes, because nothing creates JetStream state on purpose.

**And the test count cannot be read through turbo's colour codes** — every parse of it
in chapter 3.18 returned zero, including all 22 runs of its timing battery:

    NO_COLOR=1 FORCE_COLOR=0 pnpm test:integration | sed -r 's/\x1B\[[0-9;]*[mK]//g'

---

## R15 — Where does the new file's coverage pin go?

`relay-platform/vitest.coverage.config.mts`, per file, with a stated reason — the
established shape (`resume.ts` at branches 95 with three lines explaining which branch
is unreachable and why pinning 100 would mean deleting a defensive check).

The ratchet has removed code three times rather than covered it, so the pin is written
**after** the file is measured, not predicted. `services/gateway/src/session.ts`,
`fanout.ts` and `registry.ts` carry no per-file pin today; only `resume.ts`, `limits.ts`
and `meter.ts` do.

---

## R16 — Four published chapters already say what this design contradicts

**Found in analysis pass 7, by reading the published chapters — the first pass that did.** Six
passes of tooling, cross-referencing and constitution-reading went past it, which is the point
Chapter 3.18's `gaps.md` item 8 keeps making: no instrument in this repository reads prose.

    part-2/chapter-06   a ForwardRef — presence and typing "will reuse this exact pub/sub
                        plumbing with TTLs per ADR-10"
    part-3/chapter-18   ":651"  presence "needs the same missing mechanism"
                        ":1596" "Chapter 3.19 needs the same thing built for presence"
    part-3/chapter-08   ":3415" presence "needs the same" connection registry

Each is refuted by an entry in this file. R1 gives presence its own subject grammar and its own
module rather than the fan-out's plumbing. R7 shows presence needs the channel set at transition
time, not a membership push. R6 shows the connection registry is neither needed here nor correctly
specified where it is defined.

**The Vietnamese mirrors carry all four**, so it is eight files.

**Chapter 2.6's is different in kind from the other three.** The others are a predecessor's guess
about a successor, and being wrong about the future is ordinary. 2.6's is a `<ForwardRef>` — a
promise made to a Part-2 reader about what this chapter would do — and a reader who followed it
here would find a design that quietly does something else. So this chapter answers it out loud
rather than diverging in silence, which is also better teaching: the fabric is typed to messages at
three points and the third sits inside a function ten chapters fence, so the road not taken was
never "keep it simple", it was "edit the hot path".

**What this says about the passes.** Seven of them, and the finding needed a direction none of the
first six used — opening the published chapters and reading what they say about presence. Every
earlier pass compared artifacts to artifacts, artifacts to the constitution, or artifacts to code.
Prose about the future is the one surface none of those reach, and it is where chapter 3.17's most
expensive defect also lived.

---

## R17 — The gap ledger assigned this chapter two generations ago

**Found in analysis pass 12**, by following the ledger back rather than reading only the immediate
predecessor's.

    3.17 gaps.md   9 items, "Carried forward" on 7 owners
                   item 2 → "Owner: chapter 3.19. Carried forward; still open, and now it
                             has a chapter."  ← this feature, named
    3.18 gaps.md   9 items, "Carried forward" appears 0 times
    3.19           cited 3.17's ledger 0 times before this entry

Chapter 3.17 recorded presence as a declared frame with no sender, checked it rather than assuming
it — *"the only occurrence of 'presence' in `services/gateway/src` is the English word, in a comment
about cursors"* — and assigned it here. This feature's Summary argued the same point from scratch,
which is not wrong, only unprovenanced.

**The convention is what broke, not the memory.** 3.17 ran its ledger as a ledger: every item
restated, every owner re-examined, seven marked carried. 3.18 stopped. Because CLAUDE.md's header
names only the immediate predecessor, one dropped generation makes the one before it unreachable by
the path the header describes — so this is not a missing citation but a chain with a link out.

**And the numbers collide.** Item numbers are per-feature: 3.17's item 1 is the unidentified lane
flake, 3.18's item 1 is the idempotency-key mismatch. This feature cited "gaps.md item 1" meaning
the first while its own header points readers at the second. Eighteen references, eight unqualified,
one false. Third appearance of this class — after task ids across renumbers (pass 4) and FR-013
across features (pass 11).

---

## R18 — What this feature costs the lane, and the model that said otherwise

**Found in analysis pass 13**, by asking what a number costs rather than whether it is correct.

    3.18 close-out     41 files, 607 tests, mean 194.74 s against a 240 s budget — 45 s headroom
    3.19 adds          30 integration tests, all in ONE new file
    the pool           presence.itest.ts joins fanout, resume, limits, session, isolation,
                       meter and public-surface — eight files, run in PARALLEL

**The cost model this feature quoted is refuted by the baseline it cites.** `tasks.md` said the lane
*"costs per suite… cost scales with api boots"*. Chapter 3.18's `baseline.txt` measured the opposite
for the case that matters here: *"`--concurrency=1` serialises PACKAGES; vitest parallelises FILES
inside each… true across packages and **false within one**."* The api package fits 196.21 s of test
time into 102.26 s of wall clock because of it.

So the question is not whether thirty tests fit in forty-five seconds. **A pool's wall clock is set
by its slowest file**, and `presence.itest.ts` is the one file here that deliberately waits — grace
periods, a twenty-user drain, a five-connection teardown. Whether it becomes the gateway pool's
longest file is unmeasured, and the close-out battery now has to record the gateway package's own
wall clock rather than only the lane total.

**And one test could not have been built as written.** The task asking for Redis *restored* has the
obvious implementation stop the compose container — which breaks the seven suites running beside it. The repository already knew: `services/api/src/limits/limits.itest.ts:484` says *"a dead port
rather than stopping the container, because the lane runs files in PARALLEL and stopping Redis would
break every other suite mid-run"*, and **no test in this repository manipulates a container** — zero
`docker stop`/`start` matches. A dead port covers "down" and cannot cover "restored", and
`redis-server` is not installed on the lane machine, so the mechanism is an in-process TCP proxy in
front of the real Redis, closed and re-listened. The rule was written down two chapters ago; this
feature had to rediscover it by asking what a task would do when someone ran it.

---

## R19 — ADR-10 cannot be edited, and this chapter changes what it decided

**Found in analysis pass 14**, by reading the constitution's *governance* statements against the
task list. Pass 5 read its coverage statements; nothing had read these.

    constitution VII      "ADRs are immutable once accepted; superseding requires a new ADR."
    docs/05-sad.md:49     the same sentence, in the document being edited
    supersession precedent  one grep, one hit — the rule itself. No ADR has ever been amended.

Two tasks planned to rewrite ADR-10: its decision sentence in the SAD, and its **Decision** section
in the deep dive. Both called it a correction of a description.

**ADR-10's own Revisit clause refutes that.** *"Presence exceeds ~30% of gateway publish volume in
load tests — then presence subjects get their own fabric or channels opt in."* R1 gives presence its
own subject grammar now, for a reason the trigger does not name, and the chapter-notes task already
requires recording that this takes **half of ADR-10's revisit remedy before its trigger fired**. A
remedy taken early is a decision changed, not a description corrected.

**And this feature already knew the rule.** `spec.md` invokes it to reject the per-channel opt-in —
*"opting presence in per channel would need a superseding ADR"* — while two tasks planned to edit
ADR-10 in place. The rule was cited to close one door and walked through at another.

**The fix is additive and cheap.** ADR-01 through ADR-18 exist, so **ADR-19** is free. ADR-10 changes
in exactly one place, its `**Status:**` line, which already carries annotations — supersession's
normal mechanic. Its decision text, its Consequences and its deep-dive Decision section keep their
original wording, which is what a superseded record is supposed to do: **a superseded ADR still
saying what it said is the record working, not a contradiction.**