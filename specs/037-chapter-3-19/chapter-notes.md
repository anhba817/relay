# Chapter notes — 3.19, presence and who is allowed to see it

*Written during the work, not at close-out. The close-out sections — what shipped, the
phases that went badly, what the next feature should do differently, and the hand-off to
chapter 3.20 — arrive in phase 9.*

## The scoping is topology, and there is no scoping code to read

**A reader looking for the filter will not find one, and that is the design rather than an
omission.** FR-RTM-07 says a presence event reaches only users sharing at least one channel
with the subject. Nothing in `presence.ts` or `session.ts` compares two membership sets.

The rule is enforced by three facts that compose:

    a transition publishes on `presence:{channel_id}` for each of the SUBJECT's channels
    an instance subscribes to `presence:{channel_id}` only for channels its OWN members hold
    delivery walks `registry.subscribersOf(channelId)`, which is a membership test

So an instance receives a transition only on subjects it subscribed to, and it subscribed
only to channels its local members belong to. A user who shares no channel with the subject
is on no instance that hears about them — and if they happen to share an instance with
somebody who does, `subscribersOf` does not return them.

**Two consequences worth stating rather than leaving to be discovered.**

A private channel needs no special case. FR-CHN-05's third verb — *observe presence* — is
satisfied because a non-member is not subscribed, which is the same mechanism that handles
a public channel they never joined. The test for it exists anyway, because "no special case
was needed" and "the case was never considered" look identical from outside.

Cross-tenant isolation is likewise structural: presence keys carry `{env}` and channel ids
are unguessable UUIDs. That makes it the kind of property that holds until somebody adds a
scan or a pattern read, which is why the exemption in `eslint.config.mjs` is written against
the limiter's standard — every key composed from the authenticated connection's own
environment id, none read that was not composed here.

**What this costs.** The scope is exactly as correct as the subscribe set, and the subscribe
set is taken once at connect. A user who joins a channel while connected does not appear
online to that channel's members until they reconnect (FR-021). That is FR-RTM-10's
staleness wearing a different hat, and it is unfixed here on purpose.

## The chapter took half of ADR-10's remedy, and its trigger never fired

ADR-10's revisit condition, written in the SAD and again at `docs/06-adr-deep-dives.md:651`,
names two remedies and a threshold: above ~30% of gateway publish volume, *"presence
subjects get their own fabric or channels opt in"*.

**This chapter took the first remedy and closed the door on the second, and neither move was
caused by the threshold.**

Presence now publishes on `presence:{channel_id}` — its own fabric — because `chan:{id}` is
typed to messages at three points and the third is inside a function fenced by ten chapters
(R1). And SRS open question 3 closes as *not opt-in*: a per-channel toggle is a data model,
a UI, an API surface and a defaulting rule, bought to solve a volume problem nobody has
measured. Both decisions are about the shape of the code that exists. Publish volume did not
enter either argument.

**So the trigger is undischarged, and so is NFR-SCL-01.** Nothing in this chapter measured
presence as a fraction of gateway publish traffic, because the lane's largest membership set
is five channels and its largest instance count is two. The numbers this chapter does have —
`cmdstat_subscribe calls=12`, six fan-out and six presence across two instances and three
channels — describe the cost's *shape*, one subscribe per channel per instance, and say
nothing about its size at ten thousand connections.

A later reader has an easy wrong inference available: presence got its own fabric, therefore
the 30% threshold was crossed. It was not. If it is crossed later, the remedy still on the
table is the one this chapter declined — channels opting in — and the argument against it
recorded in Appendix C row 3 was made at a scale where the question could not be answered.
That argument should be re-read, not re-cited.

## The two file counts, kept apart from the start

    10   what the chapter TEACHES     -> drove the word estimate
     9   what the chapter FENCES      -> drove the chain
    11   files changed in the platform, re-derived from `git diff --name-only caeabc9`

The two disagree by exactly one file and that file is `eslint.config.mjs`, for the reason
in the next section.

**The third number came in at 11 and the phase-8 prediction was 10.** The eleventh is
`vitest.coverage.config.mts`, which phase 9 edited to carry the two presence pins — a file
the chapter neither teaches nor fences, amended by the close-out rather than by the work
the chapter is about. That is the ordinary way this number moves, and it is why the
practice says re-derive it at the very end rather than trust the plan's figure. Chapter
3.17's prediction agreed with its diff; this one is one out, in the direction a close-out
always pushes.

Outside the platform: **15 files in `relay-tutorial`** — two chapters in two locales, the
four corrected passages in two locales, three mirrored documents, `post-series.md` and
`lib/tutorial.ts` — and **4 in `docs/`**. Everything else this feature touched is both taught and fenced, which
is what a small feature looks like; the practice exists so the numbers are not conflated,
not to force them apart.

**The word estimate comes from arguments, not from the file count.** The rate is not an
estimator: 3.15 and 3.16 agreed on ~154 words per taught file, 3.17 came in at 84.7, and
3.18 at 315. This chapter makes five arguments —

    1  a frame declared in chapter 1.3 that nothing has ever produced
    2  why presence gets its own subject grammar rather than riding `chan:{id}`
    3  three 30-second numbers that turned out to be three quantities
    4  the scoping is topology; there is no filter to read
    5  a TTL expiring publishes nothing, so somebody has to be elected to say it

— and 3.18's 2,836 words over a comparable set puts the estimate near **2,500**.

**Actual: 2,445**, measured with `scripts/prose-words.mjs`. The estimate was 2.2% high.

That is one data point and it should not be read as more than one, but it is the first time
in this series the estimate was made from arguments rather than from a rate, and the rate
would have been wrong by a wide margin either way: at 3.15/3.16's ~154 words per taught file
the prediction was 1,540, and at 3.18's 315 it was 3,150. The true value sits between them
at 245 per taught file, which is a fourth rate — the point being that there is no rate.
Counting the arguments took a minute and was worth it.

## What this chapter fences, decided rather than discovered

Chapter 3.18 left `session.itest.ts` outside the chain and found out at close-out; it is
chapter 3.18's `gaps.md` item 2 and chapter 3.17's item 7, and the cost is stated in its own words — *"the
end-to-end test that proves this chapter's claim is never replayed against the
repository"*. So this is decided here, in phase 8, before a fence is written.

**All five new files are fenced, integration test included.**

    packages/protocol/src/presence.ts          60 lines   whole file
    packages/protocol/src/presence.test.ts     50         whole file
    packages/protocol/src/index.ts              +1 line   diff
    services/gateway/src/presence.ts          426         whole file
    services/gateway/src/presence.test.ts      69         whole file
    services/gateway/src/presence.itest.ts   1302         whole file
    services/gateway/src/registry.ts          +14         diff
    services/gateway/src/session.ts           +85         diff
    services/gateway/src/main.ts               +9         diff

`presence.itest.ts` is the longest single fence in the series — the previous high is
`users.itest.ts` at 916 lines — and it is fenced anyway. The series already fences
twenty-five `.itest.ts` files whole and none as diffs alone, so the precedent is not in
question; only the size is, and a size
argument is how the previous chapter arrived at an unverified test.

**`eslint.config.mjs` is the one exception, and it is a chain fact rather than a choice.**
The state that file reaches after every chapter has run is **73 lines**; the repository's is
386. The difference is `fences/post-series.md`, which owns the two restriction sets and all
three ignore lists and is applied *after* the last chapter. This chapter's edit adds one
entry to an ignore list that does not exist yet at the point a chapter could fence it — a
hunk anchored on `"services/api/src/fanout/**",` has **zero** matches in the pre-3.19
chapter state, because post-series is what puts that line there.

    node dump-state.mjs eslint.config.mjs chapters   73 lines
    node dump-state.mjs eslint.config.mjs head       386 lines, byte-identical to caeabc9

So the amendment goes to `fences/post-series.md` as a fourth `eslint.config.mjs` hunk, and
the chapter teaches the same lines as an **excerpt**. This is fence-chain rule 3 from the
other side: a chapter cannot do the appendix's work, and here the appendix already owns the
file. The excerpt is not chain-verified — chapter 3.17's `gaps.md` item 7 is that class —
but the file is:
post-series checks it as strictly as any chapter, so what is unverified is the chapter's
quotation of it, not the line itself.

## Six frame kinds, two producers

FR-RTM-05 names six real-time event kinds. All six have had frames in `frameSchema` since
chapter 1.3. Before chapter 3.18, **none of them had a producer**; 3.18 gave
`message.created` one and this chapter is the second.

    message.created      3.18 (api publisher) and 2.6 (gateway)   HAS a producer
    presence.changed     this chapter                             HAS a producer
    message.updated      nothing writes messages.edited_at        none
    message.deleted      nothing deletes                          none
    membership.changed   the writer exists; nothing publishes     none
    typing               a frame and a 5 s expiry in its comment  none

The list is written out rather than counted because chapter 3.18's spec claimed `typing`
had no frame in the union, and `typingSchema` is in `frameSchema`. An unnamed set is a set
nobody has checked.

`presence.changed`'s eighteen idle chapters have a sharper record than the schema. Chapter
3.12's direction gauntlet asserts it is refused when a client utters it — *"derived from
connections the gateway holds, not claimed"* — and that row has been green since 3.12
against a system in which the gateway derived nothing. **A test can be green about a
capability that does not exist.**

## Nine translated chapters are missing from the sitemap

Found by checking the premise of the task that adds this chapter's manifest entry: it said
chapter 3.18 sets `translatedIn` and is "the only one of the last eight" to do so. It sets
none.

    entries in lib/tutorial.ts: 35   missing translatedIn: 3.10 … 3.18   (nine)
    every one of those nine has a Vietnamese page.mdx on disk

`app/sitemap.ts:26` is the field's only consumer, and it gates whether the `/vi` URL is
emitted as its own entry. So nine Vietnamese chapters route, render and are absent from the
sitemap. The `alternates.languages.vi` hint is still emitted for them, which is why nothing
looked broken.

The field's own doc comment says it "gates all vi links". One grep says it gates one thing:
the sitemap. Both facts belong in `gaps.md`; nine manifest entries are not this chapter's to
change, and 3.19's own entry sets the field correctly.

---

# Close-out

## What shipped

    3.19 "presence, and who is allowed to see it"  10 files taught, 2,445 words, 9 fences
                                                   11 files changed in the platform,
                                                   re-derived from `git diff`
    645 integration tests across 42 files, 18 of 20 full-lane runs green
    mean 228.18 s, stdev 1.41, budget 240 — 11.8 s of headroom
    coverage: gateway/presence.ts and protocol/presence.ts both 100/100/100/100
    221 fenced files across 36 chapters, 36 translated · fence predecessor `caeabc9`

    per package, over the eighteen green runs
        api          mean 102.21 s   stdev 0.15
        dispatcher   mean  72.65 s   stdev 1.13
        gateway      mean  45.09 s   stdev 0.54     <- this feature's package

    the static page count      93 -> 95, two per chapter, measured both ends
    close codes                17, unchanged — this feature adds none
    SRS clause rows            245, unchanged — no clause changed
    figures                    226

**The gateway package's own clock is `presence.itest.ts`.** Eight files run in parallel
there and this one is the slowest, so 45.09 s is the file. That is the number to watch: it
grew 32.6 -> 45.2 s standalone when phase 9 added seven coverage tests, and the package
grew 41.91 -> 45.09.

## The battery's power, stated rather than implied

**Eighteen green runs reject a per-run failure rate above about 15% at 95% confidence, and
nothing finer.** Twenty would reject 13.91%. A 5% flake survives twenty runs 35.85% of the
time; rejecting one needs 59 runs, which no chapter here has run.

So the battery is evidence that the lane is not badly broken and is not evidence that it is
clean. **Both of this battery's failures make the point in opposite directions.** Run 1 was
contamination from the step before it — the sealed outsider's containers were still
stopping — and no number of green runs would have said so; reading the log did. Run 10 has
a mechanism, six concurrent api boots inside the gateway package, and one run in nineteen
is exactly the rate at which a battery this size tells you almost nothing about how often
it will happen next.

The useful output of twenty runs is not the pass rate. It is `stdev 1.41` on the wall clock
and `stdev 0.15` on the api package — a lane that varies by a second and a half is one where
a five-second regression is visible, and that is what the budget is for.

## The phases that went badly

**Three reds in a row that were the fixture, not the subject.** This is the single most
expensive pattern in the chapter and it recurred in four separate phases:

    phase 1   the observe-it-failing task went red on `dev-token: 401`, not on the
              missing frame. `createApiKey` returns `{ credential }`, not
              `{ plaintext }`. WHICH red it produces is that task's whole point.
    phase 2   test 1 passed, tests 2-4 reported `expected [] to have a length of 1`.
              Reads exactly like a fabric that does not cross instances. It was a
              shared fixture: a 30 s TTL left test 1's subject still online in test 2,
              so `SET … NX` correctly refused and nothing published.
    phases 3-5 an unfiltered collector caught the SUBJECT'S OWN frame — three phases
              running. Always FR-011 working; always the assertion that was wrong.
    phase 9   two new tests opened a socket for a user named `watcher`. The fixture's
              watcher is `linh`. The dev-token endpoint mints a token for any id, so
              the socket opened, the user was a member of nothing, the instance
              subscribed to nothing, and both publishes reached nobody.

The generalisation worth carrying: **when a presence test is red, check the fixture
before the fabric.** Every one of these looked like a distributed-systems failure and
none of them was.

**Two fixes that were worse than what they fixed.** R2a found that without a re-pin the
key dies up to a refresh interval before the grace ends, so a reconnection in that gap
publishes a spurious second `online`. R2b found that the first form of that fix — arming
the check at exactly `graceMs` — puts two deadlines on one instant reached by two clocks,
and when the timer wins the user is stranded online **for ever**. A cosmetic duplicate
was replaced by a permanent lie, and only measuring against a real Redis showed it.

**A test that passed while proving nothing, for four phases.** *"logs
presence.invalid_payload for a payload that is not a transition"* asserts `toEqual([])`.
It is a good test — FR-029 from the other side — under a title that claims an arm it never
touches. Both rejection arms of the module read zero coverage while it was green. Nothing
in this repository compares a test's title to its assertion, and the coverage ratchet
found it only because FR-032 pinned 100.

**An instrument of mine that lied.** The first `pnpm coverage` was invoked as
`pnpm coverage | sed … > out; echo "exit=$?" >> out` and recorded `exit=0` under nine
failures, because `$?` after a pipeline is the last command's status. Everything since
uses `set -o pipefail` and `PIPESTATUS[0]`. This is CLAUDE.md's "a checker's blind spot is
worse than its absence" one level down, in the harness rather than the repository.

**Four violations of this feature's own rule, all caught by its own checker.** Task ids
outside `tasks.md` — twice in `research.md`, once in `chapter-notes.md`, once in the
success-criteria table — plus two more in phase 9, in `chapter-notes.md` and `gaps.md`.
The rule was written in analysis pass 4 and I broke it six times. A rule with a checker is
a rule; without one it is a preference.

**Two task premises that were already false when written.** The tutorial plan was said to
name neither FR-RTM-07 nor FR-CHN-05 — it has named both since chapter 3.18's phase 8 —
and chapter 3.18 was said to set `translatedIn` when it sets none. Checking the second one
found **nine translated chapters missing from the sitemap**. Both premises were two `grep
-c`s away, and both changed what the task actually was.

**A red run is not a measurement.** Two early lane runs both reported 1m43s and neither
was a lane: turbo stops after the api package fails, so the number was the time to fail.
Run 1 of the close-out battery did it again for a different reason.

## What the next feature should do differently

**Estimate prose from arguments, and say which.** Predicted 2,500 words from five
arguments; measured 2,445. The rate would have been wrong either way — 3.15/3.16's 154
words per taught file predicts 1,540 and 3.18's 315 predicts 3,150, and this chapter's own
rate is a fourth number. Counting the arguments took a minute.

**Decide what a chapter fences in the phase that writes it, not at close-out.** Chapter
3.18 discovered `session.itest.ts` was outside the chain after tagging. This chapter
decided in phase 8, before a fence was written, and fenced all five new files including a
1,302-line integration test. The size argument is how the previous chapter arrived at an
unverified test.

**Check whether the appendix already owns a file before planning to fence it.** The state
`eslint.config.mjs` reaches after every chapter is 73 lines; the repository's is 386. A
chapter's hunk anchored on a line `fences/post-series.md` inserts matches zero times. Two
files this chapter touched are in that class, and both amendments went to the appendix with
the reason written there.

**Run the standalone number and the lane number before believing either.** Seven tests
added 12.6 s to `presence.itest.ts` standalone and 3.5 s to the gateway package, because a
package's wall clock is its slowest file and a standalone run pays for its own api spawn.
The lane total did not move. A file's cost and a lane's cost are different measurements.

**Ask what a test's title claims, not only what it asserts.** The one defect that survived
every analysis pass and four implementation phases was a title. Grep the test names for the
requirement ids and read the assertion under each.

**And use a person.** Sixth chapter, and the two most expensive findings here were both
prose a person had to read: four published claims about presence that nine analysis passes
of tooling went past, and a test title contradicting its own assertion. Every check in this
repository compares bytes.

## For chapter 3.20

**The fence predecessor is commit `d38f415`, not the tag.** `part3-ch19` will be
annotated, so `git rev-parse part3-ch19` returns the tag object and only
`git rev-parse part3-ch19^{commit}` returns the commit. Chapter 3.17 paid five wrong
answers for reading a tag instead.

    relay-platform   d38f415   test(presence): the arms a green suite left alone
    relay-tutorial   the phase-9 commit, made after this one
    relay (root)     the close-out commit, made last

**Whether anything is amended after the tag.** Chapter 3.18 had exactly one post-tag
commit, `4a49653`, and it touched only `specs/036-chapter-3-18/` — which is why 3.19's
fence predecessor was `caeabc9` and not the tag, and why that distinction had to be
written into CLAUDE.md. This chapter tags after every record is committed, so the intent is
that nothing follows it. **Verify rather than assume**: `git log part3-ch19..HEAD` in each
of the three repositories is the check, and if it returns anything touching
`relay-platform`, the fence predecessor for 3.21 is that commit rather than this one.

**Run `check:fences` rather than reading a number.** Chapter 3.18's own `chapter-notes.md`
says 216 fenced files at line 17 and 212 at line 260, and the checker settled it. This
chapter's number is **221 across 36 chapters, 36 translated**, and it is printed by
`pnpm check:fences` in `relay-tutorial` — not by any of these documents.

**What is waiting.** `gaps.md` has seventeen items with owners. Four are addressed to
whoever comes next rather than to nobody:

    item 2   FR-RTM-10, unmet on three paths now, and one membership re-read closes all three
    item 5   nine translated chapters absent from the sitemap — nine one-line edits
    item 8   this feature's two checkers die like chapter 3.18's `sweep.py` unless somebody decides
    item 17  six of the gateway's eight integration files each spawn their own api

And the unnumbered one, on its sixth chapter: `specs/036-chapter-3-18/reader-protocol.md`
still needs a second person. Two of this chapter's most expensive findings were prose —
four published claims about presence that nine analysis passes of tooling went past, and a
test title that contradicted its own assertion. **Every check in this repository compares
bytes.**
