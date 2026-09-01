# Chapter 3.21 — notes

*Decisions made during implementation, and the records the next chapter needs.*

---

## The slug (T083a)

    the-frame-nobody-may-send

Chapter 3.20's is `the-membership-that-changed`. This chapter is about a frame a
client may not send — until it may, and then only one — and an expiry nobody
announces. The slug names the first half because it is the half a reader meets
first: `session.ts` refused every inbound frame but `message.send` for twenty
chapters, and this is the chapter that opens a second door.

**No task decided this**, and it appears as `<slug>` in three others.

## The frame's name (T011, decided in phase 1)

    typing.send        { type: "typing.send", payload: { channel } }

T011 said "name it in this task and nowhere else" and sits in phase 2 — one phase
after the test that has to utter it. **A premise failure of the same shape as
chapter 3.20's phase 3**, where a task wanted a binding a phase before its
consumer. Decided in phase 1, recorded in `contracts/typing-fabric.md` in phase
2's commit.

Two arguments produced it. `typing.start` reads as a state machine with a missing
`typing.stop` — the frame this protocol deliberately does not have. And `.send`
makes the inbound set `{ message.send, typing.send }`, so **the rule is legible:
an inbound frame ends in `.send`**, which is what FR-003 means by a named set
rather than a list.

## The two counts (T082)

    14   what the chapter must fence      -> drove the chain
     9   what the chapter teaches         -> drove the word estimate

**Never let either do the other's job.** The fence set is 9 files the chain
demands plus 5 this chapter creates; the taught set is the 9 that carry an
argument. The third count — files changed — is re-derived from `git diff` at the
very end and is expected to disagree with both.

## The port ranges (T083c)

**Recorded in `gaps.md`, not fixed here.** The lane's port map at the top of
`services/gateway/src/limits.itest.ts` lists seven ranges and the lane has nine:
`presence.itest.ts` holds 4700–4900 (chapter 3.19) and `membership.itest.ts` holds
5400–5600 (chapter 3.20), and neither registered.

**The cost is why.** Chapters 3.08 and 3.13 both fence that file, so two comment
lines mean regenerating two chapters' diffs — for a defect neither chapter this
one is about introduced. `typing.itest.ts` needs no range at all (`server.listen(0)`),
so this chapter neither uses the map nor adds to it.

**Named, with an owner: the next chapter that takes a range.** Do not leave it
unnamed a third time.

## The FR-RTM-08 verdict (T104a)

Recorded in ADR-22 rather than only here — see phase 9. **Met on the platform's
half, delegated on the client's, with the delegation named as a boundary rather
than a completion.**

## A ForwardRef describes what the next chapter must decide (T087)

Chapter 3.20 published two claims this chapter falsifies, and one of them is its
ForwardRef: *"the first that can reuse a grammar rather than adding one"*. It
predicted a conclusion. **A ForwardRef should describe what the next chapter must
decide, not what it will conclude** — and chapter 3.21's own, in T085a, names what
3.22 must decide about a per-member expiry rather than guessing the structure.

---

## What shipped

    3.21 "the frame nobody may send"
                                    9 files taught, 2,306 words, 18 fenced blocks
                                    14 files fenced (9 the chain demanded + 5 new)
                                    18 platform files changed, re-derived from
                                       git diff: +2,559 -26
                                    13 tutorial files changed
    twenty-run battery: 19/20 green
    lane mean 228.63 s, stdev 0.68, budget 240 — 11.37 s headroom
    44 files, 727 tests · gateway package 45.38 s (stdev 0.45)
    coverage: both new production files 100/100/100/100
    234 fenced files across 38 chapters, 38 translated · 99 static pages
    predecessor `ba5e3d6`

FR-RTM-08 is closed with its boundary named rather than asserted, and FR-RTM-05
has four of six producers. `message.updated` and `message.deleted` wait on a
surface that does not exist — chapter 3.23.

## The phases that went badly

**PHASE 11 FOUND THE FEATURE DID NOT WORK.** `main.ts` built the typing module,
awaited its `close()`, and never passed it to `attachSessions`. Everything else was
green: 174 gateway integration tests, 1,174 coverage tests, both new files pinned
at 100/100/100/100, a `/healthz` advertising eleven frames, and a seam that
accepted `typing.send`. `signalTyping` called `typing?.publish(...)` on `undefined`
and the optional chain made it silent.

**Found by the sealed outsider client — the only check here that talks to a built
image rather than importing source.** Analysis pass 10 had noticed that file
contained zero `.send(` calls and called it a coverage gap; it was a product gap.

**PHASE 2's PREMISE WAS WRONG ABOUT ITS OWN FAILURE.** T009 predicted
`unknown_frame_type` and close 4002 for a typing signal "today". A type absent from
the union fails `safeParse` first, so the answer was `invalid_frame` with the socket
open. The refusal has three states, not two, and the task list described the middle
one as the first.

**PHASE 4's NAMED SET COST THE UNION'S NARROWING.** Three `TS2339`s forty lines
below the seam. The single `!==` had been refusing types *and* narrowing the
discriminated union, and a predicate over the type string still does not narrow —
it has to take the frame.

**T098 FOUND FOUR TEST TITLES THAT OUTRAN THEIR ASSERTIONS, ALL MINE, ALL WRITTEN
IN THIS PHASE.** One quoted FR-015's clause while the body refuted it. Two moved a
coverage number while asserting nothing — `expect(true).toBe(true)` and no
`expect` at all.

**FIVE INSTRUMENTS CRIED WOLF, ALSO ALL MINE.** A waiter that fired on the api's
own `"level":"error"` lines; a filter that read a complete file as empty;
`sweep.py`'s task count falling to 127 when nine boxes were checked; `sweep.py`'s
skip list swallowing a real hit; and a traceability matcher reporting 28 false
gaps. Every remedy was the same: name the set, do not guess the pattern.

## What the next feature should do differently

**A DEFERRED BINDING NEEDS A TASK.** Phase 3 deferred a destructuring to keep the
phase committable and recorded the wiring as a later task's job. No later task had
it, and three things hid the hole: the module was built, its `close()` was awaited
so lint saw a use, and the call site was optional so absence was not a crash.
**"A later phase will do it" is not an owner.**

**RUN THE SEALED CLIENT BEFORE THE LAST PHASE.** It is the only check against a
built artifact, and it ran once, at the end, and found the chapter's largest
defect. Running it after the MVP phase would have found it six phases earlier.

**A FIXTURE THAT NAMES A MONTH WHILE ITS SUBJECT READS THE CLOCK HAS AN EXPIRY
DATE.** One api test broke at midnight UTC on 1 September, mid-close-out, in a file
this chapter never touched. A battery spanning that boundary would have filed it as
a 5% flake.

**ONE RED RUN COSTS A FIFTH OF A BATTERY'S POWER.** Twenty green rejects a failure
rate above 13.91%; 19 of 20 rejects only 21.61%, which does not reject chapter
3.20's measured 17.5%. **"19 of 20 green" reads better than it measures.**

## The hand-off for chapter 3.22

**The fence predecessor is a commit, not a tag:**

    git rev-parse part3-ch21^{commit}

`part3-ch21` is annotated, so `git rev-parse part3-ch21` returns the tag object.
This chapter's own predecessor was `ba5e3d6`, obtained the same way.

**Tagged, and the value is `0ecb21f`:**

    relay-platform   part3-ch21 -> 0ecb21f   test(3.21): keep the meter fixture's
                                             child output (gaps item 9)
    relay-tutorial   part3-ch21 -> 3009af7   docs(3.21): regenerate chapter 21's
                                             fences after the wiring fix
    root             part3-ch21 -> the last close-out commit on `main`

**The two submodule hashes are quoted and the root's is not, and that asymmetry is
the point.** The submodule commits are what the fence chain needs and what the
root's tree names — verified with
`git ls-tree part3-ch21^{commit} relay-platform relay-tutorial` rather than
assumed. The root's own hash cannot be written down here: T106 states why — *a
record of a commit hash inside the commit it names does not converge* — and the
first attempt at this paragraph proved it, quoting `49cb482` and then being
overtaken twice while the close-out finished, once by T107's own checkbox and once
by a checker fix. Naming the root tag by its ROLE is true after every such commit;
naming it by its hash was false within the hour.

Neither submodule tag moved for any of it. This is the same shape as chapter 3.20's
note that a feature's tail can amend a file after tagging, and it is why the
predecessor is a commit rather than a tag.

**Nothing is pushed.** All three repositories are ahead of `origin/main`, and the
three tags exist on one machine until somebody pushes them with the branches,
submodules first.

**3.22 builds FR-RTM-09's five-connection cap, and its first job is a decision.**
The SRS describes `conn:{env}:{user}` as a Redis set with one TTL, and a TTL is per
key rather than per member — one instance refreshing the key keeps a dead
instance's entry alive for ever. **What that chapter must decide is how a
per-member expiry is expressed**, and whatever structure it picks, the argument it
owes is why the members expire independently. This chapter's ForwardRef says that
and does not guess the structure, which is the rule chapter 3.20's ForwardRef broke.

**Read `gaps.md` first** — nine new items, twenty-five carried with their status
re-checked. Item 4 is addressed to 3.22 directly: the lane's port map lists seven
ranges and the lane has nine, and the next chapter to take a range owns it.
