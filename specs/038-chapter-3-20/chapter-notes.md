# Chapter notes — 3.20, the membership that changed under a live socket

*Decisions this chapter made that are not visible from the code, and the reasons.
Written as the phases run.*

---

## `check-refs.py` was carried forward rather than rewritten (Phase 1)

Chapter 3.19's `gaps.md` item 8 asked what happens to a feature's own checkers: its
two die the way chapter 3.18's `sweep.py` died — written for one feature, useful in
the next, and deleted with the directory because nobody decided.

**This chapter's answer is to copy the file and reset `FOREIGN`.** Not to promote it
to a repository-level script, which would make it a thing to maintain for chapters
that do not want it; not to import it across directories, which makes one feature's
record depend on another's. A copy with its declarations emptied is a checker that
starts each chapter saying nothing it has not been told.

The copy is not free. Phase 4 found the pattern rejecting `T054a` outright —
`T\d{3}` with no suffix — although chapter 3.17 shipped `T012a`, `T047c` and `T054b`.
A carried-forward checker carries its blind spots forward too, and the fix
(numeric-part sequencing, orphan suffixes caught, four red tests) belongs to whoever
copies it next.

---

## An unban publishes nothing (Phase 7)

A ban revokes every channel through `member:{env}:{user}`. **The unban does not
restore them, and that is a decision rather than an omission.**

`banUser` sets `users.banned_at` and leaves the `members` rows alone, so an unbanned
user's memberships are exactly what they were. What the ban destroyed is the live
connection's `channelIds`. Restoring it would need the api to re-derive the channel
list and publish an `added` frame per channel — the per-channel shape
`contracts/membership-fabric.md` rules out for the ban itself, reintroduced for its
rarer inverse.

Two mechanisms already repair it:

- **reconnecting**, which reads membership at the door (chapter 3.2). Asserted in
  `membership.itest.ts`, and it is what a client does after being cut anyway.
- **the backstop's periodic re-read**, which picks the memberships up within its
  interval without a reconnect.

So the answer to "does delivery resume without a reconnect?" is: not immediately, and
yes within the backstop's interval. The socket stays open throughout — a ban is not a
protocol violation and close code 4009 is not this.

**What this costs:** an unbanned user with a live socket sees nothing until one of
those two fires. For a moderation action measured in minutes or hours, a re-read
interval measured in seconds is not the part anybody notices.

---

## The ban's sentinel never reaches a client (Phase 7)

`contracts/membership-fabric.md` carried one open question — `channel: "*"` or a
separate payload shape — and the phase that decided it took neither. The fabric
carries `"*"`; the **gateway expands it** into one wire frame per channel that
connection holds. A client receives what N individual removals would have produced.

The objection the contract raised against `"*"` was that a sentinel inside a
`z.string().min(1)` reads as a channel id for a year. It survives in the fabric
payload and in the `membership.published` log line, both internal, with
`ALL_CHANNELS` as its one spelling. It does not survive to a customer.

---

## The verdict on FR-RTM-10 (Phase 8)

FR-014a permits two honest outcomes and forbids a third. The third — editing the
clause until the code passes — is what chapter 3.18 refused on this same clause:
*"a specification edited until it matches the code has stopped being a
specification."*

**FR-RTM-10 is met, and the qualification is a bound rather than an exception.**

    on the happy path      34 ms, 88 ms, 87 ms      budget 5,000 ms
    with the fabric lost   one backstop interval    60,000 ms

The five-second clause is met by the publish, measured at 57x margin. When the
publish is dropped — a severed fabric, a Redis restart, a partition — the
revocation still lands, through the periodic re-read, within sixty seconds rather
than within five.

**So under fabric loss the clause is exceeded by 55 seconds, and that is stated
here rather than hidden in an interval nobody wrote down.** It is not the
happy-path-only outcome FR-014a describes as the fallback: the revocation is
guaranteed, not abandoned. What is bounded is how late it can be.

Three things make this the right trade rather than a shortfall dressed up:

- **Five seconds and sixty seconds are budgets for different events.** The clause
  gives a working mechanism five seconds to take effect. The backstop bounds the
  damage of a mechanism that did not run at all, which is rarer by orders of
  magnitude. `baseline.txt` carries the arithmetic: five seconds against
  NFR-SCL-01's 10,000 connections per instance is 2,000 requests per second per
  instance, which is a poll wearing a backstop's name.
- **Constitution IV is satisfied in the form it asks for.** It permits a lossy
  fabric *"precisely because durability and resume live in PostgreSQL sequences
  and cursors"* and requires any new mechanism to preserve that recovery
  property. A message recovers through its resume cursor; a revocation has none,
  so the re-read is its cursor. Without it this chapter would be publishing
  revocations onto a fabric that is allowed to drop them, with nothing behind it.
- **Both halves are tested, and both bite.** The happy path is
  `session.itest.ts`'s inverted FR-RTM-10 test, still waiting its own 5,500 ms.
  The loss path is four tests in `membership.itest.ts` that fail within five
  seconds when `membership?.watch(…)` is removed.

**What a reader should not take from this:** that sixty seconds is a number
anybody measured a requirement against. Nothing in the SRS bounds a post-loss
revocation. Sixty is what the connection budget affords, and if a clause is ever
written for that case, this is the number it has to argue with.

---

## The SRS did not change, and Appendix C gained nothing (Phase 9)

`git diff docs/04-srs.md` is **empty**. Not "no clause row changed" — no byte changed.
Research R10 expected that and expecting is not verifying, so it is checked here
where a reader can re-run it:

    git diff --numstat docs/04-srs.md      (no output)
    git diff docs/04-srs.md | grep -cE "^[+-]\| \*\*(FR|NFR|EIR|DR|CON)"     0

FR-RTM-05, FR-RTM-10, FR-WHK-02, FR-CHN-04 and FR-006 already said what this
chapter built. That is the outcome FR-002 asks for and the one chapter 3.18
named the alternative to: *"a specification edited until it matches the code has
stopped being a specification."*

**Appendix C is unchanged too, and that is a decision rather than an oversight**
(FR-002a). Its six open questions are about sequence numbering, the thousand-member
ceiling, presence opt-in (closed by 3.19 as question 3), metering precision, the
dev-token endpoint's rate limit, and emoji pack sharing. **None is about
revocation, and this chapter does not open one.**

It could have. The question it would open — *what bounds a revocation the fabric
dropped?* — is answered here by a number nobody specified: sixty seconds, chosen
from the connection budget. That is recorded in ADR-20 with its arithmetic and its
revisit trigger, which is where a decision with a cost and no clause belongs. An
open question is for a choice the product has not made; this is a choice made and
written down, waiting for a clause to disagree with it.

**One clause of this chapter's own spec did change** — FR-032, from three log names
to four — and the amendment is written into `spec.md` with the argument. That is a
feature specification, not the SRS.

---

## What this chapter fences, decided before a fence was written (Phase 10)

**The chain decides most of it, not preference.** `pnpm check:fences` at HEAD
reported 18 problems before a word of the chapter existed — 18 files this chapter
edited that earlier chapters or the appendix already fence. Every one must be
re-fenced here or the reconstruction stops being valid. That list is not a choice:

    eslint.config.mjs                              packages/protocol/src/index.ts
    services/api/src/channels/channels.controller.ts    …/channels.module.ts
    services/api/src/db/repository.ts              …/internal/internal.module.ts
    services/api/src/isolation/targets.ts          …/isolation/targets.itest.ts
    services/api/src/outbox/event.ts               …/outbox/outbox.itest.ts
    services/api/src/users/users.controller.ts     …/users/users.module.ts
    services/api/src/users/users.service.ts        services/gateway/src/api-client.ts
    services/gateway/src/main.ts                   services/gateway/src/resume.itest.ts
    services/gateway/src/session.ts                services/gateway/src/session.test.ts

**The choice is the nine new files**, which nobody fences yet. Five are fenced in
full because they are what the chapter teaches — the protocol module, the api's
publisher and its module, the revived controller, and the gateway's module. Two
unit tests are fenced in full because they are short and because a test nobody
can read is a test nobody checks.

**`services/gateway/src/membership.itest.ts` is an excerpt, and that is a cost.**
It is over a thousand lines and would be a third of the chapter. An excerpt-only
file is **never verified against the repository at all**. That is
chapter 3.19's `gaps.md` item 7, recorded there for `sentinel.ts`, `sentinel.sql`
and `guard.itest.ts`; this adds a fourth. Taken deliberately: the alternative is a
chapter whose bulk is a test file, and the file is exercised by the lane on every
run whether or not a fence watches it.

### The appendix owns four of them, and one entry sits inside its hunk

`fences/post-series.md` carries hunks for `eslint.config.mjs`,
`services/api/src/db/repository.ts`, `services/api/src/outbox/outbox.itest.ts`
and `services/gateway/src/resume.itest.ts`.

The eslint one is the sharp case. Its hunk inserts a block between
`"services/gateway/src/fanout.ts",` and the list's closing `],` — and this
chapter's `"services/gateway/src/membership.ts"` entry lands **inside** that
inserted region, as chapter 3.19's `presence.ts` entry did before it. A chapter
hunk anchored on a line the appendix inserts matches zero times, which is what
this chapter's own task list warned about and what chapter 3.19 answered by
fencing `eslint.config.mjs` as an **excerpt**. The same answer here, for the same
reason: an excerpt is `NOT_A_FILE` to the checker, so it never joins the chain
and never fights the appendix for an anchor.

### The two counts, kept apart

    9    what the chapter teaches   -> drives the word estimate
    27   what the chapter fences    -> drives the chain (18 required + 9 new)
    29   files changed              -> re-derived from `git diff --name-only`
                                      against `d38f415` at the end

Three numbers, three jobs, and none of them asked to do another's. Chapter 3.17
established the practice with 16/27/35; the gap between 27 and 29 here is
`services/api/src/outbox/event.test.ts` and
`services/gateway/src/session.itest.ts`, which this chapter changed and nobody
fences — the second being chapter 3.18's own recorded gap.

---

## What twenty green runs actually prove (Phase 11)

**A per-run failure rate above 13.91%, rejected at 95% confidence. Nothing finer.**

If a suite fails with probability *p* per run, twenty independent green runs have
probability (1−*p*)²⁰. Setting that to 0.05 gives *p* = 1 − 0.05^(1/20) = 0.1391. So
twenty green runs are consistent with a flake that fails one run in eight.

    a 5% flake survives twenty green runs   35.85% of the time
    rejecting a 5% flake at 95% confidence  needs 59 runs
    twenty runs reject                      p > 13.91%

**Chapter 3.17 ran twenty-six and failed once**, mechanism unidentified, and left it
unfixed on exactly this reasoning: one failure in twenty-six is not evidence of a 4% flake
rather than a 1% one, and chasing it would cost more runs than the information is worth.
That is chapter 3.19's `gaps.md` item 12, carried here.

**What the battery is for, then.** Not "the lane is reliable" — twenty runs cannot say
that. It is for the failures a single run cannot show: an ordering dependency between
files, a fixture that survives one run and not two, a port that is free until it is not.
Those either appear within twenty runs or are rarer than this instrument can see, and
saying which is the honest report.

**And it measures the machine as much as the code.** Chapter 3.19 lost its run 1 to
containers a previous step was still stopping; chapter 3.12's first attempt failed at run
11 to two Next.js dev servers, with no port held and no `EADDRINUSE`. The battery here was
started after `docker compose stop api gateway dispatcher` returned, and nothing else was
run on the machine while it was going.

---

# Close-out

## What shipped

**FR-RTM-10 is met.** The clause has been unmet since chapter 2.6 and a test in
`session.itest.ts` has asserted the violation on purpose since 3.18, carrying the
instruction for whoever fixed it: *"change this to `.rejects` on the day a re-read
exists."* That test is inverted, its 5,500 ms wait unchanged, and its title with it.

**FR-RTM-05's third event kind has a producer.** `membership.changed` has been in the
protocol union since chapter 1.3 with nothing emitting one. Three of six kinds now
have producers; the other three are named in the chapter with the reason each waits.

**FR-WHK-02 gains two of its eight event types** — `channel.member_added` and
`channel.member_removed` — which is the durable record constitution II requires beside
the publish. No endpoint subscribes to either yet.

**A third subject grammar, with two shapes** (ADR-20). A removal rides
`member:{channel_id}` and reaches the remaining members and the removed user in one
publish, because the removed user is still a member at that instant. An addition
cannot, so `member:{env}:{user}` exists — the first event in this system addressed to
a **principal** rather than a channel.

**A backstop, because ADR-07's permission does not cover this payload.** That record
allows a lossy fabric on the grounds that a dropped message is recovered by its
cursor. A revocation has no sequence and no cursor, so a sixty-second re-read stands
in for one, applied through the same function a published change takes.

**Chapter 3.19's presence staleness closes as a consequence.** A mid-connection join
subscribes `chan:`, `presence:` and the channel's membership subject together, so both
halves of that staleness close with one mechanism — which is why 3.19 said the debt
belonged to the session layer rather than to presence.

## The phases that went badly

**Two ordering requirements had no observable difference, and both were specified as
requirements.** Two tasks each asked for the proof that an ordering bites: remove it,
watch a test fail. Neither failed. The send-before-cut is unobservable because the
notice goes to a socket reference the function already holds; the subscribe-before-insert
is unobservable because `subscribersOf` returning a connection changes nothing while
the instance is not subscribed. **Both were found only by running the proof the task
asked for.** What FR-008 actually forbids is deriving the audience *after* the
mutation — that implementation was built, and it fails the file's first test in five
seconds with no notice at all.

**A test passed with its subject deleted, twice, for two unrelated reasons.** The
FR-029 buffer test presented a cursor equal to the buffered frame's sequence, so the
resume marks dropped it — a test about the resume under a title about revocation. Then
the connection was not buffering at all: that window is one backfill round trip, about
twenty milliseconds. Slowing the fabric does not widen it, because a failed fabric
confirmation calls `degrade()`, which empties the buffer itself.

**Three tasks specified a binding, a fixture and an exemption a phase too early.**
One wanted `membership` destructured before its consumer existed; one wanted the api
harness two phases before its caller; and an ioredis exemption went to the eslint list
that flat config overrides for `.itest.ts`. All three fail a gate the same phase runs.

**The collector was unfiltered for the fourth time across two chapters.** This feature's own task list says
"filter every collector by subject" and cites the three phases of 3.19 it caught. The
cross-kind assertion counted by type anyway and read two `presence.changed` where a
watcher correctly sees their own arrival.

**A published sentence stopped being true and no checker could see it.** ADR-07's deep
dive says a lost pub/sub frame "heals identically" to a lost WiFi packet. True of every
payload that fabric carried when it was written; false of this one. Found by grepping
for a *claim* rather than for a symbol.

## What the next feature should do differently

**Falsify an ordering claim before writing its test.** A task that says "the ordering
is the requirement" is asserting an observable difference. This chapter wrote two such
tasks and neither survived. The check is cheap — swap the lines, run the suite — and it
belongs before the test, not after.

**List a module's arms in the phase that builds it.** Three of this chapter's four new
production files reached 100/100/100/100 on the first coverage run because phase 3
enumerated the arms and drove them there. Chapter 3.19 met its equivalents at close-out
and paid seven tests, a deleted branch and a re-measured battery.

**Ask where a route's coverage is measured, not just whether it is tested.**
`memberships.controller.ts` had five integration tests and read 28.57%. The suite runs
in another package.

**Read the map the other way at close-out, every time.** It found a requirement with
no test — the same shape chapter 3.18 found for FR-007 — and two rows describing a
proof technique that proved nothing.

**Share a negative window before writing the second one.** Two 5.5-second waits for the
same clause were a third of the file's wall clock. Two tasks said so in advance, in writing,
and the second wait was written anyway.

## Hand-off to chapter 3.21

**The fence predecessor is a commit, not the tag.** `part3-ch20` is annotated, so
`git rev-parse part3-ch20` returns the tag object; `git rev-parse part3-ch20^{commit}`
is what a fence chain needs.

**`gaps.md` has 24 items.** Four are addressed to a next chapter rather than to nobody:
item 11 (nine translated chapters absent from the sitemap — nine one-line edits), item
15 (seven of nine gateway integration files spawn their own api, worse by one this
chapter), item 17 (`session.itest.ts` outside the fence chain, edited by two consecutive
chapters), and item 20 (two comments claiming a missing ioredis listener kills the
process, which a measurement contradicts).

**The typing indicator is the natural next chapter.** It is the one remaining kind of
FR-RTM-05's six that can reuse `chan:{channel_id}` rather than adding a grammar, and
FR-RTM-08 brings a five-second expiry and a rate limit with it.

**USE A PERSON.** `specs/036-chapter-3-18/reader-protocol.md` is now named by seven
consecutive chapters and run by none.

---

## The metrics

    3.20  "the membership that changed under a live socket"
          9 files taught, 2,999 words, 27 fenced (18 the chain demanded + 9 new)
          31 files changed in the platform, re-derived from git diff

    two twenty-run batteries      17/20 and 16/20 green
    lane   mean 228.50 / 228.77   stdev 1.25 / 0.50    budget 240
    gateway package               45.50 / 45.48        stdev 0.15 / 0.22
    43 files, 701 tests
    229 fenced files across 37 chapters, 37 translated
    coverage: all four new production files 100/100/100/100

**FORTY RUNS, SEVEN FAILURES, AND NEITHER MECHANISM IS THIS CHAPTER'S.** The observed
rate is 17.5%, which twenty green runs would have rejected — so a chapter reporting
"twenty green" about this lane would have been reporting luck. The two mechanisms are
the rate limiter's wall-clock-aligned fixed window and a gateway api fixture failing
under contention in three different files, and both are in `gaps.md` with owners.

That is the honest close-out number, and it is worse than chapter 3.19's 18 of 20 and
chapter 3.17's 25 of 26 **without the lane having got worse** — those are all
consistent with one rate that none of the three batteries could distinguish.

## What is left

**Nothing is pushed.** All three repositories are ahead of `origin/main` — the root,
`relay-platform` and `relay-tutorial` — so `part3-ch20` exists on one machine until
somebody pushes it with the branches. Submodules first, then the superproject, or the
root's gitlinks name commits the remotes do not have.

**The fence predecessor for 3.21 is a commit, not the tag.** `part3-ch20` is
annotated, so `git rev-parse part3-ch20` returns the tag object;
`git rev-parse part3-ch20^{commit}` is what a fence chain reads.
