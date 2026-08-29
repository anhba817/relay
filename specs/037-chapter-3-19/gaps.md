# Open things — chapter 3.19

Seventeen, each with an owner. Eight are carried forward with their status re-checked
rather than copied; nine are new.

**Every reference carries its chapter, because the numbers collide.** Chapter 3.17's
item 1 is an unidentified lane flake and chapter 3.18's item 1 is the idempotency-key
mismatch; "item 1" alone names neither. Chapter 3.18 carried none of its predecessors'
items forward, which is why chapter 3.17's ledger is reachable from here only by
someone who knows to look for it — CLAUDE.md's header names one predecessor.

---

## 1. Presence has no snapshot, so a roster starts empty — NEW, and it is this chapter's

**Owner:** unassigned, and it is the first thing anybody building a UI on this will ask
for.

A client that opens a socket learns about transitions from that moment and nothing about
the state before it. There is no `GET /v1/channels/:id/presence` and no frame carrying a
roster. Every presence design needs it eventually; the shape is a read, not a stream, and
it is a decision rather than an omission. Stated in the chapter so a reader meets it
rather than discovers it.

## 2. A user who joins a channel while connected is invisible there — FR-RTM-10, CARRIED

**Owner:** unassigned. **Chapter 3.18's item 4 assigned this to chapter 3.19 and its
stated reason does not hold.**

That item says *"Presence needs the same missing mechanism — something that tells a
gateway a membership changed"*. It does not. Presence needs the subject's channel set at
the moment of a transition, and `POST /internal/session` already supplies it (research
R7). What presence inherits is the staleness, not the requirement: the subscribe set is
taken once at connect, so a channel joined mid-connection carries no presence for that
user until the socket reopens.

**Run rather than assumed**, this chapter's close-out:

    npx vitest run --config vitest.integration.config.mts -t "FR-RTM-10"
    Test Files  1 passed | 7 skipped (8)      Tests  1 passed | 102 skipped (103)

`session.itest.ts:677` — *"keeps delivering to a member who was REMOVED while connected
(FR-RTM-10)"* — still passes, which is the violation still being asserted. The clause is
P1 and unmet on three paths now: socket sends (2.6), REST sends (3.18) and presence
(this chapter). The fix is a membership re-read in the session layer, and it closes all
three at once.

## 3. A test whose title claimed an arm it did not touch — NEW

**Owner:** closed here, and recorded because the class is not.

*"logs presence.invalid_payload for a payload that is not a transition"* asserted
`toEqual([])`. It publishes a message on a message subject and checks that presence never
sees it — FR-029 from the other side, a good test under a false name. Both of the
module's rejection arms read **zero** while it was green, through six analysis passes and
four phases.

Renamed, and the two real tests written. The class survives: **nothing compares a test's
title to its assertion**, and a title is what a later reader greps for when asking
whether a path is covered. The coverage ratchet is the only instrument that caught it,
and only because FR-032 pinned 100.

## 4. The refresh re-election restores the key and publishes nothing — NEW

**Owner:** unassigned. Cheap, and it needs one field.

When the presence key is lost under a live connection — a Redis restart, an eviction —
the refresh loop finds `SET … XX` answering null and puts the key back. It publishes no
`online`, because the loop holds `held`, a user and an environment, and a publish needs
the subject's channel set. `presence.suppressed` says so rather than leaving it silent.

**The window this leaves is real.** Between the key vanishing and the next refresh — at
most `refreshMs`, ten seconds by default — another instance's grace check can find the
key absent and publish `offline` for a user who is connected here, and no `online`
follows it. That user appears offline until they next transition, which for a connected
user may be a long time. FR-031 permits the duplicate `online` that would close it.

Carrying `channelIds` on `held` alongside the environment id is the whole fix. Not taken
here: it changes the module's shape at close-out, after the battery had measured the
committed tree.

## 5. Nine translated chapters are absent from the sitemap — NEW

**Owner:** unassigned, and it is nine one-line edits.

`lib/tutorial.ts` gates the Vietnamese URL on `translatedIn`, and chapters **3.10 through
3.18** each shipped a Vietnamese `page.mdx` without setting it. Nine pages route, render,
and never appear in `sitemap.xml`. Nothing looked broken because `alternates.languages.vi`
is emitted for every published chapter regardless.

Found by checking a task's premise. The task that adds this chapter's manifest entry said
chapter 3.18 sets the field and is "the only one of the last eight" to do so. It sets none.

And the field's own doc comment overstates it — *"Gates all vi links"* — where one grep
says it gates exactly one thing, `app/sitemap.ts:26`. Chapter 3.19's entry sets it
correctly; the nine are not this chapter's manifest to change.

## 6. `conn:{env}:{user}` is specified as a shape that cannot work — NEW (research R6)

**Owner:** whoever builds FR-RTM-09's concurrent-connection cap.

`docs/05-sad.md` specifies the connection registry as a Redis **set** of instance ids with
a 60 s heartbeat-refreshed TTL. A Redis TTL is per key, not per member, so one live
instance refreshing the key keeps a dead instance's entry alive for ever. A sorted set
scored by heartbeat time and pruned with `ZREMRANGEBYSCORE` on read is the shape that
works.

The SAD now says so at the row itself, and chapter 3.8's published claim that *"Presence
needs the same registry"* is corrected in both locales — presence asks a yes-or-no
question of one key's existence and needs no registry at all.

## 7. Two fenced files instruct a Redis port that is not listening — NEW (research R13)

**Owner:** unassigned. Both files are fenced by chapters 2.6 and 2.7.

`services/gateway/src/fanout.itest.ts:18` and `services/gateway/src/resume.itest.ts:26`
both carry `RELAY_REDIS_PORT=16379 pnpm --filter @relay/gateway test:integration` while
the line below defaults to 6379. Measured: 16379 refused, 6379 open on redis 8.10.0.

The published chapters are not wrong — 16379 is chapter 1.2's documented override for a
host that already runs its own Redis. The two comments present one valid invocation as
though it were the only one. The fix is a conditional clause in a comment.

## 8. The fate of this feature's two checkers — NEW, and a decision is the point

**Owner:** the author, and it should be settled before chapter 3.20 rather than after.

`specs/037-chapter-3-19/check-refs.py` and `check-prose.py` are feature-local. Both proved
themselves: `check-refs.py` caught four violations of this feature's own no-task-ids rule,
and `check-prose.py` turned FR-033's "inspection only" into a command that goes red.

**Chapter 3.18's `sweep.py` is the precedent for doing nothing:** discussed in its
`chapter-notes.md`, given no owner in its `gaps.md`, and referenced nowhere outside its
own feature directory since. Two of these die the same way unless someone decides.

The honest split: `check-refs.py` is about a spec-kit feature directory and belongs with
the skill or nowhere. `check-prose.py` is about published prose, which is the repository's
oldest uncovered surface (chapter 3.17's item 8), and its claim list is per-feature — a
general version would be a claims file that every chapter appends to, and that is a
feature, not a move.

## 9. The lane is not idempotent from cold JetStream state — CHAPTER 3.18's item 3, CARRIED

**Owner:** unassigned. Reproduced here in a new place.

Chapter 3.18 measured it under `pnpm test:integration` after `docker compose down -v`.
This chapter hit it under **`pnpm coverage`**, with the stores up the whole time: nine
`dispatcher.itest.ts` deliveries failed on the first coverage run, the dispatcher package
alone then passed 16/16, and the second coverage run passed 1034/1034. `pnpm coverage`
runs every suite in one vitest process, so the file order differs from turbo's package
order and the suite that creates the stream may not run first.

The fix is unchanged: a bootstrap step that calls `ensureStream` before the lane.

## 10. A fourth file outside the fence chain — CHAPTER 3.18's item 2, CARRIED

**Owner:** unassigned. **Not repeated by this chapter, which is the change.**

`session.itest.ts` is still fenced by no chapter. Chapter 3.19 decided its own fencing in
phase 8 rather than discovering it at close-out, and fenced all five new files including
`presence.itest.ts` at 1,302 lines — the longest single fence in the series. The general
fix is still a fenceable shared test harness.

`eslint.config.mjs` and `vitest.coverage.config.mts` are the inverse case and not this
gap: both ARE in the chain, via `fences/post-series.md`, and this chapter teaches lines it
cannot fence because the appendix owns the file. The excerpt is unverified; the file is
not.

## 11. Three files permanently outside the chain — CHAPTER 3.17's item 7, CARRIED

**Owner:** unassigned. Untouched by this chapter.

`sentinel.ts`, `sentinel.sql` and `guard.itest.ts` are excerpt-titled and outside the
chain by construction. Chapter 3.17's seven unclaimed files, `README.md` among them, are
also unchanged — and `README.md` is still the quickstart of record that no chapter teaches
and no checker verifies. This chapter read it to run the sealed outsider, which is the
only reason it was exercised at all.

## 12. A twenty-six-run battery failed once, mechanism unidentified — CHAPTER 3.17's item 1, CARRIED

**Owner:** whoever next touches `services/api/src/quotas/quota-relay.ts`.

`quotas.itest.ts > "cannot fail a send when the mail server is gone"` returned 14 where
`drainOnce` should return 0. Not reproduced by this chapter's battery. Deliberately
unfixed: changing code until a symptom stops, with no mechanism in hand, buries the
defect.

This chapter's battery has the same power as every one before it and the arithmetic is in
`chapter-notes.md`: twenty green runs reject a per-run failure rate above 13.91% at 95%
confidence and nothing finer.

## 13. Two comments claim a missing ioredis listener kills the process — CHAPTER 3.18's item 5, CARRIED

**Owner:** unassigned. `services/api/src/limits/store.ts:137` is fenced by chapter 3.8.

Measured wrong by chapter 3.18 and still wrong. This chapter's `presence.ts` attaches its
two listeners for the accurate reason instead — unstructured, unbounded output defeats
NFR-OBS-01 — and says in its comment that the limiter's stated reason does not transfer.

## 14. The two entrances accept different idempotency keys — CHAPTER 3.18's item 1, CARRIED

**Owner:** unassigned. Untouched: presence carries no idempotency key.

## 15. A rate-limit header assertion compares two whole seconds with `>` — CHAPTER 3.18's item 9, CARRIED

**Owner:** unassigned, and still cheap. `services/api/src/limits/limits.itest.ts:113`.

Not taken here for chapter 3.18's own reason, one chapter later: the battery has measured
the committed tree, and a twentieth changed file after that measurement would mean the
battery no longer describes what ships. It was not observed in this chapter's runs.

## 16. Two published counts disagree, and a spec claimed a frame did not exist — NEW

**Owner:** unassigned, and both are chapter 3.18's records rather than its code.

`specs/036-chapter-3-18/chapter-notes.md` says **216** fenced files at line 17 and **212**
at line 260. `check:fences` settles it — 216 at that tag, 221 now — and CLAUDE.md's header
for this chapter had to say "run, not read".

`specs/036-chapter-3-18/spec.md` claims `typing` has no frame in the union. `typingSchema`
is in `frameSchema` and has been since chapter 1.3. This chapter names all six of
FR-RTM-05's kinds explicitly, in the chapter and in `chapter-notes.md`, because an unnamed
list is a list nobody has checked.

## 17. Six of the gateway's eight integration files each spawn their own api — NEW

**Owner:** unassigned, and this chapter added the sixth.

Run 10 of the close-out battery failed with `isolation.itest.ts`'s `beforeAll` timing out
at 90 s on `api = await startApi()`. The gateway package took 101.02 s in that run against
a mean of 45.09. No assertion failed: an api process took more than ninety seconds to
answer `/health`.

    limits.itest.ts   meter.itest.ts   public-surface.itest.ts
    isolation.itest.ts   presence.itest.ts   session.itest.ts

vitest runs files in parallel inside a package, so that is six concurrent api boots on one
machine. `presence.itest.ts` already solves this within itself — one `startApi()` at file
level for seven describes, which is worth 21 s of the file's own time — and the same move
across files needs a shared fixture the lane can own.

**This is a mechanism, which is what separates it from chapter 3.17's item 1.** Observed at
1 in 19 legitimate runs; rejecting a 5% rate would need 59 runs and was not attempted. Not
fixed at close-out, for chapter 3.18's reason: the battery has measured the committed tree.

---

## The one that is not numbered, because five chapters have numbered it

**A person reading the documentation.** Named by chapters 3.14, 3.15, 3.16, 3.17 and 3.18
and closed by none of them; chapter 3.18 made it runnable —
`specs/036-chapter-3-18/reader-protocol.md`, one engineer who has not read the specs, 45
minutes, six questions — and still nobody ran it.

**Owner: the author, and it needs a second person.** No command in this repository can
discharge it. Every check here compares bytes, and this chapter is the fourth consecutive
one whose most expensive findings were prose a person had to read: four published claims
about presence that nine analysis passes of tooling went past, and a test title that
contradicted its own assertion.
