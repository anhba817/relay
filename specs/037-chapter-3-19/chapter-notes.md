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

    10   what the chapter TEACHES     -> drives the word estimate
     9   what the chapter FENCES      -> drives the chain
    10   files changed                -> re-derived from `git diff --name-only` at close-out

The two disagree by exactly one file and that file is `eslint.config.mjs`, for the reason
in the next section. Everything else this feature touched is both taught and fenced, which
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
`gaps.md` item 2 and item 7 there, and the cost is stated in its own words — *"the
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
file. The excerpt is not chain-verified (`gaps.md` item 7's class), but the file is —
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

Found by checking T098's premise, which said chapter 3.18 sets `translatedIn` and is "the
only one of the last eight" to do so. It sets none.

    entries in lib/tutorial.ts: 35   missing translatedIn: 3.10 … 3.18   (nine)
    every one of those nine has a Vietnamese page.mdx on disk

`app/sitemap.ts:26` is the field's only consumer, and it gates whether the `/vi` URL is
emitted as its own entry. So nine Vietnamese chapters route, render and are absent from the
sitemap. The `alternates.languages.vi` hint is still emitted for them, which is why nothing
looked broken.

The field's own doc comment says it "gates all vi links". One grep says it gates one thing:
the sitemap. Both facts belong in `gaps.md`; nine manifest entries are not this chapter's to
change, and 3.19's own entry sets the field correctly.
