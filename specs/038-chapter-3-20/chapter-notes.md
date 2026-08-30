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
