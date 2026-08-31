# Gaps — chapter 3.20

*Every gap this chapter leaves, and every gap it inherited, each with a status that was
re-checked rather than copied. Chapter 3.17 carried seven of nine forward without
re-checking; chapter 3.18 carried none that way, and this ledger follows 3.18.*

**Each reference names its chapter, because item numbers are per-feature and collide.**
Chapter 3.17's item 1 is a flake; chapter 3.18's item 1 is the idempotency keys.

---

## THIS CHAPTER'S OWN

## 1. A dropped publish is repaired in sixty seconds, not five — NEW

FR-RTM-10 gives a mechanism five seconds. The publish meets it at 34–88 ms measured. When
the publish is **dropped** — a severed fabric, a Redis restart, a partition — the backstop
repairs it within its interval, and that interval is sixty seconds.

So under fabric loss the clause is exceeded by fifty-five seconds. **The revocation is
guaranteed; what is bounded is how late it can be.** No SRS clause bounds a post-loss
revocation, and ADR-20 carries the arithmetic: five seconds against NFR-SCL-01's 10,000
connections per instance is 2,000 requests per second per instance.

**Owner:** whoever writes a clause for the post-loss case. Sixty seconds is the number it
has to argue with, and the trade is a request rate, not an implementation.

## 2. Two ordering requirements had no observable difference — NEW

This chapter's task list specified send-before-cut (FR-008) and subscribe-before-insert
(FR-010) as requirements, and asked for the proof that each bites. **Neither swap failed
anything.** Both were unobservable, and the second was checked with the window widened to
1.5 s to be sure.

The lesson is recorded in the chapter and in `baseline.txt`, but the *class* is open: a
task list can specify an ordering whose failure mode does not exist, and nothing catches it
except running the proof.

**Owner:** the next feature that writes an ordering requirement. Falsify the claim before
writing the test, not after.

## 3. A message published inside the subscribe window is lost — NEW

Between an add committing at the api and the gateway's `fanout.subscribe` landing, that
instance is not receiving the channel. A message published then does not reach the new
member over the socket. It is in Postgres and history returns it, so nothing is permanently
lost — but "you are a member, delivery starts" has a gap the width of a Redis round trip.

`membership.itest.ts` asserts the loss, so a change that closes it turns that test red and
has to say what it did. Closing it properly needs the api to hold its publish until every
gateway acknowledges a subscription, which is a round trip on an administrative path and a
new failure mode for news the reader can already fetch.

**Owner:** undecided, deliberately.

## 4. A fenced file edited for a reason this chapter does not teach — NEW

`services/api/src/outbox/outbox.itest.ts` is fenced by chapters 3.3 and 3.17 and by
`post-series.md`. Two of chapter 3.3's crash invariants counted every outbox row in an
environment — the same question while `message.created` was the only type — and the walk's
own seed calls `addMember`, so they now measure a membership row. Both are scoped to
`payload->>'type' = 'message.created'`, which is what they always meant.

**Owner: DISCHARGED IN PHASE 10.** This chapter fences the file. Recorded here because it
was found in phase 2 and a fence cost discovered at close-out is chapter 3.18's item 2
repeating.

## 5. `membership.itest.ts` is an excerpt, and excerpts are never verified — NEW

Over a thousand lines, and fencing it in full would make a test file a third of the
chapter. An excerpt-only fence is `NOT_A_FILE` to `check-fence-chain.mjs` — **it is never
compared against the repository at all.** Chapter 3.19's item 7 records the same for
`sentinel.ts`, `sentinel.sql` and `guard.itest.ts`; this is the fourth.

**Owner:** whoever decides whether a fence chain should cover test files at all. The
honest options are to fence them in full and accept the page weight, or to say in the
appendix that test files are outside the chain by policy. Neither is a chapter's decision.

## 6. FR-032 was amended, and an amended clause is a thing to watch — NEW

The clause said the membership path's log vocabulary is exactly three names. The gateway's
delivery half emitted six. Four are gone — `rejected` folded into `failed`, `revoked_all`
deleted, `revoked` and `granted` collapsed into one `membership.applied` — and the clause
now says four, with the argument written into `spec.md`.

This is not the amendment chapter 3.18 refused: that one would have narrowed FR-RTM-10
until the code passed. This kept the clause's purpose — closed, exhaustive, tested name by
name — and corrected a count taken before half the path existed. **It is still an
amendment, and a reader should be able to find it.**

**Owner:** nobody. Recorded so that "the spec was edited" is never a discovery.

---

## CARRIED, WITH THE STATUS RE-CHECKED

## 7. Presence has no snapshot on connect — CHAPTER 3.19's item 1, UNCHANGED

A client learns transitions from the moment it connects and nothing about the state before
it, so a roster starts empty and fills in as people move. This chapter touches delivery
scope, not the roster.

**Owner:** the chapter that gives presence a read endpoint or a connect frame.

## 8. A user who joins a channel while connected is invisible — CHAPTER 3.19's item 2, **CLOSED HERE**

The subscribe set was taken once at connect, so a mid-connection join reached neither
delivery nor presence. This chapter's addition path subscribes `chan:`, `presence:` and the
channel's membership subject together, and a test asserts a co-member's arrival observed
over a channel joined mid-connection.

**Both halves of chapter 3.19's staleness close with one mechanism**, which is why that
chapter said the debt belonged to the session layer rather than to presence.

## 9. A test title that claims an arm it does not touch — CHAPTER 3.19's item 3, **RECURRED**

3.19's instance was fixed in 3.19. **The class recurred in this chapter and was caught by
the same reading**: a ban test titled "stops both channels, tells the user per channel, and
leaves others alone" no longer asserted the stop — that half had moved to the shared
five-second window — and two other titles claimed counts that lived in a `waitFor` rather
than an `expect`. All three reconciled.

**Owner:** every close-out. Nothing compares a title to an assertion, and this is the
second consecutive chapter where reading them side by side found something.

## 10. The refresh re-election restores the key and publishes nothing — CHAPTER 3.19's item 4, UNCHANGED

A presence key lost under a live connection is restored by the next refresh, and no
`online` is published for a user who never appeared to go offline.

**Owner:** the chapter that gives presence its snapshot — a roster read makes the
divergence visible and therefore worth fixing.

## 11. Nine translated chapters are absent from the sitemap — CHAPTER 3.19's item 5, UNCHANGED AT NINE

Verified rather than assumed: chapters 3.10 through 3.18 each ship a Vietnamese body with
no `translatedIn: ["vi"]`, so nine Vietnamese pages route and none appears in the sitemap.
**3.20 does not become a tenth** — its entry carries all three Vietnamese fields.

    part-3 entries without translatedIn: 3.10 … 3.18   (nine)

**Owner:** nine one-line edits, and no chapter's to make alone.

## 12. `conn:{env}:{user}` is specified as a shape that cannot work — CHAPTER 3.19's item 6, UNCHANGED

FR-RTM-09's five-connection cap rests on a Redis *set* with one TTL, and a TTL is per key
rather than per member — one instance refreshing it keeps a dead instance's entry alive for
ever. A sorted set scored by heartbeat and pruned on read is the correct version. **This
chapter names it in the published prose** as one of the things it does not do.

**Owner:** the chapter that builds FR-RTM-09, and it is a design change before it is an
implementation.

## 13. Two fenced files instruct a Redis port that is not listening — CHAPTER 3.19's item 7 (its research R13), UNCHANGED

## 14. The fate of a feature's own checkers — CHAPTER 3.19's item 8, **ANSWERED HERE**

Chapter 3.18's `sweep.py` died with its directory; 3.19 asked what happens to a checker
written for one feature and useful in the next. **This chapter's answer is to copy the file
and reset `FOREIGN`** — not to promote it to a repository script, which makes it a thing to
maintain for chapters that do not want it, and not to import across feature directories,
which makes one record depend on another's.

The answer is in `chapter-notes.md` with its cost: a carried-forward checker carries its
blind spots too. This one rejected `T054a` outright — `T\d{3}` with no suffix — although
chapter 3.17 shipped `T012a`, `T047c` and `T054b`. Fixed here and tested red four ways.

## 15. Seven of the gateway's nine integration files spawn their own api — CHAPTER 3.19's item 17, **WORSE**

Now **seven of nine**. This chapter adds `membership.itest.ts` with its own `startApi()`,
and its task list said so in as many words before the file existed: no cross-file fixture
exists to share, building one is item 17's actual fix and a job of its own, so the decision
was to pay the seventh spawn and say so.

    7 of 9 gateway integration files spawn an api

**Owner:** a shared fixture, which is a feature rather than a chapter's tail. The counter
moves the wrong way once per chapter until somebody builds it.

## 16. Three files permanently outside the fence chain — CHAPTER 3.17's item 7, **NOW FOUR**

`sentinel.ts`, `sentinel.sql`, `guard.itest.ts`, and now
`services/gateway/src/membership.itest.ts`. See item 5 above; they are the same gap counted
from two directions and the owner is the same.

## 17. A fourth file outside the chain — CHAPTER 3.18's item 2, UNCHANGED

`services/gateway/src/session.itest.ts` is fenced by nobody. **This chapter edited it** —
the FR-RTM-10 test is inverted there — so the file has now been changed by two consecutive
chapters without a fence noticing either.

**Owner:** whoever fences it. The cost of not doing so rises every chapter.

## 18. The lane is not idempotent from cold JetStream state — CHAPTER 3.18's item 3 via 3.19's item 9, UNCHANGED

## 19. The rate limiter's fixed window crosses under a loaded machine — CHAPTER 3.17's item 1 via 3.19's item 12, **MECHANISM IDENTIFIED**

Chapter 3.17 ran twenty-six and failed once, mechanism unidentified. This chapter's
battery failed on the same class and the mechanism is now nameable.

`limits.itest.ts` — *"two environments carry DIFFERENT configured limits, each at its own
number"* — sends three requests and expects the third to be refused:

    AssertionError: expected 201 to be 429

The limiter is a fixed window **aligned to the wall clock**:
`rl:{scope}:{operation}:{windowStartMs}`, with
`windowStart = Math.floor(now / windowMs) * windowMs`. If a boundary falls between the
second send and the third, the counter resets and the third is allowed. Under a loaded
machine the gap between those sends is not microseconds, and the failure rate follows
that gap divided by the window.

**Owner:** whoever owns `services/api/src/limits/limits.itest.ts`. The fix is a test that
pins the clock or asserts the pair rather than the third request — not a change to the
limiter, which is behaving as `bucket.ts` documents.

## 19a. A gateway integration file's api fixture fails, in three different files — NEW

**Five failures across forty battery runs, in three files, all the same shape.** A
file-level `beforeAll` spawns an api; the api does not come up or stops answering; every
test in that file or describe fails at once at 0–5 ms, which is a fixture's signature
rather than a behaviour's.

    battery 1 runs 16, 17   session.itest.ts     ECONNREFUSED on its own 4400-range port
    battery 3 run 13        presence.itest.ts    the whole file
    battery 3 run 15        session.itest.ts     the same two tests as battery 1
    battery 3 run 19        isolation.itest.ts   the gauntlet describe, 15 skipped

**This is chapter 3.19's item 15 costing runs rather than merely being untidy.** Seven of
nine gateway integration files spawn their own api on a random port, vitest runs the files
in parallel, and under that contention one of them intermittently fails to become or stay
healthy. No per-file change explains three files failing identically.

A port collision was found and fixed while investigating and is **not** the cause:
`membership.itest.ts` had taken `isolation.itest.ts`'s range exactly, then overlapped it
again on the second attempt. The failing ports in `session.itest.ts` belong to that file
alone.

**Owner:** the shared api fixture chapter 3.19's item 15 asks for. It is the fix for all
five occurrences, and it is a feature rather than a chapter's tail.

## 19b. `createFanout` has no ioredis `error` listener, and this chapter made it audible — CHAPTER 3.18's R10, UNCHANGED

    [ioredis] Unhandled error event: Error: connect ECONNREFUSED 127.0.0.1:38513

Ephemeral ports, so this is a TCP proxy severing a fabric — `presence.itest.ts` has one and
this chapter added a second in `membership.itest.ts`. The client with no listener is
`createFanout`'s. Both rate limiters have one and both explain why; the fan-out does not.

The process survives — chapter 3.18 measured that against ioredis 6.0.0 — so these lines
are noise rather than a failure. But they are unstructured and unbounded, which is exactly
the NFR-OBS-01 argument every module this chapter wrote used to justify its own listener.

**Owner:** one listener in `services/gateway/src/fanout.ts`, with the reason this chapter's
modules already state.

## 20. Two comments claim a missing ioredis listener kills the process — CHAPTER 3.18's item 5 via 3.19's item 13, UNCHANGED

The measurement says otherwise: ioredis 6.0.0 prints `[ioredis] Unhandled error event: …`
and the process continues. **This chapter's new modules carry the corrected reason** — the
listener exists for NFR-OBS-01, because those lines are unstructured and unbounded — so the
tree now holds both the accurate version and the two inaccurate ones.

**Owner:** two comment edits, in `services/gateway/src/limits.ts` and
`services/api/src/limits/store.ts`.

## 21. The two entrances accept different idempotency keys — CHAPTER 3.18's item 1 via 3.19's item 14, UNCHANGED

## 22. A rate-limit header assertion compares two whole seconds with `>` — CHAPTER 3.18's item 9 via 3.19's item 15, UNCHANGED

---

## THE ONE THAT IS NOT NUMBERED, BECAUSE SIX CHAPTERS HAVE NUMBERED IT

**`specs/036-chapter-3-18/reader-protocol.md` has still not been run by a person.**

Chapters 3.14, 3.15, 3.16, 3.17, 3.18 and 3.19 each named this gap. 3.18 made it runnable —
forty-five minutes, six questions — and nobody ran it. This chapter is the sixth to name it
and the sixth to leave it.

**Every check in this repository compares bytes.** And this chapter's two most expensive
findings were not byte comparisons: an ordering requirement whose failure mode did not
exist, found by running a proof and reading the result; and a published sentence in ADR-07's
deep dive that stopped being true because the code moved underneath it, found by grepping
for a claim rather than for a symbol.

**Owner: a second person.** No command discharges this.
