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

## 046-2 · SC-007 WAS NOT RUN, AND THAT IS THE FIFTEENTH TIME

One person who has not read this specification, given the published chapter and nothing
else, answering three questions in their own words. `specs/036-chapter-3-18/reader-protocol.md`
is the procedure: 45 minutes, six questions, one person.

**It did not happen.** Fourteen records named this gap before this one.

It matters more here than usual. **This chapter's argument changed twice during
measurement** — the neighbour effect was falsified, then the index's benefit was
falsified — and the prose was rewritten each time by the person who took the
measurements. Nothing in either repository can say whether the argument in the prose is
the argument the numbers support. Every check compares bytes.

## 046-3 · THE CHAPTER IS TAGGED `part4-ch1` — AND PART 3'S COLLISION IS STILL OPEN

**DECIDED: Part 4 uses the ordinary convention, `part4-chN`.** No `rework/` prefix — that
was a rebuild artefact and it does not carry into new work. `part4-ch1` is cut as an
annotated tag on `04fe516a`, matching `part3-chN`'s object type (Part 1 and 2's are
lightweight; Part 3's are annotated).

**WHAT THE DECISION DOES NOT SETTLE.** Twenty-one stale `part3-chN` tags still point into
the replaced history:

    part3-ch18          54b2cd53      the replaced history
    rework/part3-ch18   3732d6cf      the published chapter

Both exist. `README.md:8` promises one tag per chapter and every SKIP AHEAD box names
one, so a reader following a published address today lands on a different chapter than
the one they are reading. Twenty-one stale `part3-chN` tags sit beside twenty-seven
`rework/*`.

`README.md:8` promises one tag per chapter and every SKIP AHEAD box names one. So the
namespace is now **consistent for Parts 1, 2 and 4 and wrong for Part 3**: a reader
following `part4-ch1` lands where they should, and one following `part3-ch18` lands on a
chapter that was replaced.

**That is a Part 3 problem, not this chapter's**, and it has three possible answers —
delete the stale twenty-one, retarget them at the rebuilt commits, or leave them and say
so on the `whats-moved` page. It is open.

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
