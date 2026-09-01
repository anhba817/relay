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
