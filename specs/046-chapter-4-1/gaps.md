# gaps.md — chapter 4.1

What this feature found and did not close. Numbered for citation by later chapters.

## 046-1 · THE RECONCILIATION'S TWO SIDES DIVERGE ON A DELETED USER — MOVEMENT IV INHERITS IT

`messages.user_id` is nullable, and FR-USR-05 keeps a deleted user's messages "as
authored by a deleted user". Meanwhile `repository.ts:3551` says of user deletion:
*"`usage_active_users` IS UNTOUCHED (FR-029). Billing history does not vanish with a
user."*

So `count(DISTINCT m.user_id)` drops NULLs silently while the operational set keeps its
row. **After a deletion the two sides of FR-ANL-06's 0.1% reconciliation disagree by
construction.** The corpus plants null senders at a configurable ratio so the chapter
that builds the reconciler meets this rather than discovering it.

Filed at research R4, before a line of the reconciler exists.

## 046-2 · THE READER PROTOCOL IS RETIRED, NOT DEFERRED — CLOSED

**DECIDED 2026-09-13: dropped.** Fifteen records named this gap and none closed it. A
sixteenth entry saying "still open" would have been an intention, not a plan.

**THE ARGUMENT IS ABOUT COST, AND IT HOLDS.** A chapter's tag is cut on `relay-platform`
and its prose lives in `relay-tutorial`. Chapter 4.1 contributes **0 titled fences** to the
chain — `check-fence-chain.mjs:77` collects a fence only when it matches `title="…"`, and
the close-out delta was 0. So a prose correction after publication moves no platform
commit, invalidates no tag, and re-runs no chain. **Feedback on the writing arrives from
readers and is applied then.**

A gate earns its cost when the thing it guards is expensive to change. This one guards
prose, and prose here is cheap.

**WHAT IS GIVEN UP, STATED PLAINLY.** No instrument in these three repositories now reaches
comprehensibility at all. `check-refs` compares ids, `check-chapter` compares bytes,
`check-lane-scope` reads SQL text. The specific risk this chapter carried — **its argument
changed twice during measurement and the prose was rewritten each time by the person
holding the numbers** — is accepted rather than mitigated, and will be caught by a reader
or not at all.

CLAUDE.md's "USE A PERSON" section is amended to record the decision rather than repeat
the intention.

## 046-3 · THE TAG NAMESPACE IS CONSISTENT AGAIN — CLOSED

**Part 4 uses `part4-chN`.** No `rework/` prefix: that was a rebuild artefact and does not
carry into new work. `part4-ch1` is cut as an annotated tag on `04fe516a`, matching
`rework/part3-chN`'s object type.

**AND THE TWENTY-ONE STALE `part3-chN` TAGS ARE DELETED, LOCAL AND REMOTE.** They pointed
into the history the rework replaced, so a reader following `README.md:8`'s promise of one
tag per chapter — or any published SKIP AHEAD box — landed on a chapter that no longer
exists at that address. `part3-ch18` resolved to `54b2cd53`, a different chapter from the
`rework/part3-ch18` a reader was holding.

    relay-platform   21 local · 19 remote  ->  0
    relay-tutorial   10 local ·  8 remote  ->  0
    relay            10 local ·  8 remote  ->  0

**Nothing was lost, and that was checked after the deletion rather than assumed before
it.** Every one of the 21 commits is reachable from `backup/pre-main-move-20260911`, which
is on the remote in all three repositories. `rework/part3-chN` (26) are untouched.

**THE DIVERGENCE IS EXACTLY WHERE CLAUDE.md SAYS.** `git merge-base main
backup/pre-main-move-20260911` is `6b3423d6 feat: milestone the tuan test - chapter 2.8` —
every Part 2 tag is on `main`, every Part 3 tag was not. The claim had never been checked
against the tags themselves.

## 046-4 · TWO GATES PART 4 NEEDS BEFORE ITS FIRST CHAPTER SPLITS

`docs/12-part-4-structure.md` §6 records both and neither was built here:

- **`check:redirects` as a standing gate.** Part 4 keeps the global ordinal, so a chapter
  that splits at its word ceiling renumbers the tail. `check-redirects.py` is what makes
  that safe and it ran once, by hand, inside a closed feature.
- **A gate refusing a chapter ordinal in `relay-platform` source.** SC-002 took 1,429 such
  references to 0 by hand; FR-008 states the rule and nothing enforces it.

## 046-5 · ALL SIX PYTHON INSTRUMENTS ARE STILL WIRED TO NOTHING, AND ONE OF THEM PROVED IT

`check-redirects.py`, `check-movements.py`, `check-map.py`, `check-lane-scope.py`,
`check-refs.py` and `check-chapter.py` live in `specs/045-part-3-rework/` and are
referenced by no `package.json` script and no CI step.

**`vi-placeholder.py` made the point concretely.** Run against a Part 4 chapter it dies
with `AttributeError: 'NoneType' object has no attribute 'group'`, because it matches
`id="(3\.\d+)"`. It is a Part 3 instrument in a closed feature's directory. It was copied
here and generalised by one character class rather than edited in place — which means
there are now two copies, and the next part will make three.

## 046-6 · FR-ANL-08'S BAR IS NOT CLEARED BY THIS CHAPTER, AND THE EASY CASE IS THE ONE MEASURED

FR-ANL-08 asks for ninety days of one tenant's data inside two seconds at p95. At 585.9
ms, a million rows clears it. NFR-SCL-03 puts the platform at a thousand messages a
second — ninety days of that is 7.5 billion rows — and FR-ANL-01 wants an event per
**API request**, not per message.

**The volume this chapter measured is the easy case**, and the chapter says so. The bar
belongs to the store the next chapters build.

## 046-7 · THE NEIGHBOUR EFFECT IS UNRESOLVED RATHER THAN ABSENT

The send path is 6.8 ms faster beside 102 analytical queries than alone, reproducibly,
on two schemas, with four control loops agreeing inside 1.3 ms. The measurement is
sound; the explanation is not in it.

Ten sends a second is the ceiling `DEFAULT_LIMITS.send` allows, one backend on ten cores
is not contention, and a 179 MB table fits in cache. **What this chapter establishes is
that the neighbour effect is not the argument at this volume** — not that it never
happens. Resolving it needs either a rate-limit override (FR-RTL-04 permits one) or a
corpus that does not fit in memory.

## 046-8 · THREE PART 1 TAGS POINT AT COMMITS ON NEITHER `main` NOR THE BACKUP

Found while verifying 046-3's deletion set, and deliberately not acted on.

    part1-ch1   680ce7a4   not on main   NOT IN BACKUP
    part1-ch2   e73e06d6   not on main   NOT IN BACKUP
    part1-ch3   b7291250   not on main   NOT IN BACKUP
    part1-ch4   624312ba   ON MAIN       in backup

**Those three tags are the only thing keeping those commits reachable.** `part1-ch4` and
every Part 2 tag are fine, so whatever rewrote them stopped at chapter 1.4 — most likely
the stack refoundation, which predates every record in this directory.

This is older than Part 3's rework and unrelated to it. **Deleting them would lose the
commits**, which is the opposite of what deleting the Part 3 tags did, and it is why they
were left alone. Someone should decide whether Part 1's tags should be re-cut against
`main` or whether those three commits still matter.
