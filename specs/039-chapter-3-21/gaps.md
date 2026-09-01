# Chapter 3.21 — gaps

*Every item has an owner. Every reference names its chapter, because the numbers
collide: chapter 3.17's item 1 is a flake and 3.18's item 1 is the idempotency
keys.*

**Chapter 3.20's twenty-five items are carried below with their status re-checked
against the tree rather than copied.** Carrying an item forward without
re-checking is copying.

---

## 1. A DEFERRED BINDING HAD NO OWNER, AND THE FEATURE WAS INERT — NEW, CLOSED

`main.ts` built the typing module, awaited its `close()`, and never passed it to
`attachSessions`. `signalTyping` called `typing?.publish(...)` on `undefined` and
the optional chain made it a silent no-op: eleven frames advertised on `/healthz`,
`typing.send` accepted at the seam, nothing published, nothing logged, no socket
closed.

**174 gateway integration tests, 1,174 coverage tests and two files pinned at
100/100/100/100 all passed while the feature did not exist in the product**,
because every one of them injects `typing` directly into `attachSessions`.

Found by `pnpm test:outsider` — the only check in this repository that talks to a
built image rather than importing source.

**Owner: closed in this chapter.** The item is here because the CLASS is open:
phase 3's task deferred the destructuring to keep the phase committable and
recorded the wiring as "T051's job"; T051 is *measure the subscription cost*. **A
deferred binding needs a task, and "a later phase will do it" is not one.**

Three things hid it, and each is worth knowing separately:

    the module IS built in main.ts        so the wiring looks done
    close() IS awaited in shutdown()      so lint sees a used variable
    typing?.publish is optional           so a missing option is not a crash

## 2. A FIXTURE NAMED A MONTH WHILE ITS SUBJECT READ THE CLOCK — NEW, CLOSED

`services/api/src/internal/usage.itest.ts` credited connection-minutes to a
hardcoded `"2026-08-01"` while `session.controller.ts:104` asks
`periodOf(new Date())` whether the cap is spent. **Correct until midnight UTC on 1
September 2026, and failing during this chapter's close-out** in a file this
chapter never touched.

Now `const PERIOD = periodOf(new Date())`. **Only one of the five api files that
hardcode a period had the crossing** — the others pass the period explicitly, or
test `periodOf`'s arithmetic, or use it as filler in a constraint row.

**Owner: closed.** Recorded because the timing is the lesson: a twenty-run battery
started on 31 August and finished on 1 September would have logged this as a flake
at a 5% rate, and three hypotheses would have been measured before anyone ran
`date`.

## 3. FR-015 ASKS FOR ONE LOG LINE AND THE CODE CANNOT GIVE ONE — NEW, OPEN

Severing the fabric produces **five** `typing.failed` lines with
`op: "connection"` — one per reconnect attempt per client — and **zero** with
`op: "publish"`, because ioredis's offline queue accepts the command and resolves
it when the connection returns. So a severed fabric DELAYS a typing signal rather
than dropping it.

FR-015's first two clauses hold and are asserted. Its third — *"MUST be logged
once with a stable event name"* — is satisfied by nothing per outage while the
retry logging is unbounded.

**Owner: whoever bounds the retry logging, and it is a cross-module decision.**
All four fabric modules share the listener shape: `fanout.ts`, `presence.ts`,
`membership.ts` and `typing.ts`. Bounding it in one would diverge from three.

## 4. THE LANE'S PORT MAP LISTS SEVEN RANGES AND THE LANE HAS NINE — NEW, OPEN

`services/gateway/src/limits.itest.ts`'s map is cited by `isolation.itest.ts:73`
and `public-surface.itest.ts:61` as the authority. Missing:
`presence.itest.ts` 4700–4900 (chapter 3.19) and `membership.itest.ts` 5400–5600
(chapter 3.20). **Two consecutive chapters took a range and neither registered
it**, and a 78%-complete registry is worse than none because it is consulted and
believed — it is why chapter 3.20 collided twice.

**Owner: the next chapter that takes a range.** Chapters 3.08 and 3.13 both fence
that file, so two comment lines cost two chapters' regenerated diffs. This chapter
needed no range at all (`server.listen(0)`), so it neither used the map nor added
to it. **Do not leave it unnamed a third time.**

## 5. EIR-WS-07 IS SATISFIED BY AN ADVERTISEMENT, NOT A DOCUMENT — NEW, OPEN

*"The protocol shall be fully documented, including reconnection, ordering, and
backfill semantics"*, P2, verified by inspection. The clause appears twice in the
repository, both times inside the SRS, and **no published document is a protocol
reference** — `sync-docs.sh` publishes the vision, the personas, the journey map,
the SRS, the SAD, the ADR deep dives and the error reference.

What does exist is the gateway's `/health`, which returns
`protocol: { frames, close_codes }` derived from `@relay/protocol` and current by
construction. It carries no payload shapes, no semantics and nothing about
reconnection, ordering or backfill, so it does not discharge the clause.

**Owner: whoever writes the protocol reference.** The gap predates this chapter;
**this chapter is the first to widen it**, adding the first new inbound frame in
twenty chapters to a surface with no reference document. ADR-22 carries the
client's timer obligation and is not a substitute for the frame's shape.

## 6. `sweep.py` NEEDS AN OWNER OR A RECORDED ABSENCE — NEW, OPEN

Written during analysis pass 14 because **four of thirteen findings were one
correction landing in some artifacts and not others**. It compares the phase order
and MVP marker across `plan.md` and `tasks.md`, every superseded phrasing this
chapter corrected, stated counts against measured ones, foreign requirement ids,
and placeholders. Tested red five ways; four fired.

**Owner: undecided, and that is the item.** Chapter 3.18's `sweep.py` died unowned
and is chapter 3.19's item 8, answered the same way twice. Two candidates: it
graduates to `relay-tutorial`'s `check:*` scripts as the first instrument that
compares a claim across two documents, or it stays a per-chapter file each chapter
copies with its own phrase list — which is what `check-refs.py` already is.

## 7. THE PHASE GATES DO NOT RUN THE UNIT LANE — NEW, CLOSED

Measured during analysis pass 18: `pnpm lint` 3.5 s, `pnpm typecheck` 3.4 s,
`pnpm turbo run test --force` **5.9 s** over eleven packages. The third was at no
phase gate, and 100 gateway unit tests guard `session.ts`, which five phases edit
— including `resume.test.ts`'s suppression cases, the only oracle for the seam
chapter 3.6 got wrong.

**Owner: closed in this chapter**, in nine of ten commit tasks. Phase 9 is the
documented exception: it edits prose in two trees and no TypeScript, so
`check:docs` is its gate.

## 8. CHAPTER 3.20's ITEMS, RE-CHECKED
------------------------------------------------------------

    3.20 item  status against the tree today
    ---------  ----------------------------------------------------------------
    1          the post-loss clause — UNCHANGED, still nobody's
    2          an ordering requirement whose failure mode does not exist —
               UNCHANGED. **This chapter wrote no ordering requirement**, so the
               obligation to falsify before testing had nothing to bite on.
    3          a message published inside the subscribe window — UNCHANGED
    4          `vitest.coverage.config.mts` fenced by the appendix — DISCHARGED
               AGAIN here, as a sixth hunk
    5          whether a fence chain should cover test files — UNCHANGED
    6          FR-RTM-09's unworkable `conn:{env}:{user}` shape — UNCHANGED, and
               it is chapter 3.22's first decision. This chapter's ForwardRef
               names it as a decision rather than predicting the structure.
    7          excerpt-only fences never verified — UNCHANGED. This chapter added
               three `(excerpt)` fences and they are unverified by construction.
    8          the two checkers dying unowned — see item 6 above
    9          the spec was edited — nobody's, unchanged
    10         presence's read endpoint — UNCHANGED
    11         a title compared to an assertion — **RE-OPENED AND CLOSED**: T098
               found FOUR in this chapter's own files, two of which moved a
               coverage number while asserting nothing. Nothing compares a title
               to an assertion, and the only instrument is a person reading them
               side by side.
    12         presence's snapshot — UNCHANGED
    13         nine translated chapters absent from the sitemap — UNCHANGED for
               3.10–3.18; this chapter's entry has all three vi fields
    14         FR-RTM-09 is a design change — see item 6
    15         seven of nine gateway files spawn their own api — **UNCHANGED**,
               because this chapter's tenth file spawns none. The count is seven
               before and seven after.
    16         a shared api fixture — UNCHANGED, and item 15 is why it matters
    17         `limits.itest.ts` unfenced — UNCHANGED
    18         the wall-clock rate-limit window — UNCHANGED, and it failed once
               in this chapter's gate run
    19         the same, as a flake class — UNCHANGED
    19a        four unexplained api-fixture failures — **PARTLY ADDRESSED.** The
               reason they are unexplained is that the evidence is thrown away:
               `session.itest.ts` piped stdout and stderr and read neither. Both
               pipes now feed a 200-line ring, the child's exit code and signal
               are appended, and `waitForHealth`'s timeout carries the tail. **The
               failure rate is unchanged; the next occurrence will name its
               cause.** It recurred twice in this chapter — `ECONNREFUSED
               127.0.0.1:4517`, inside that file's own range.
    19c        a green e2e package is not evidence the resume seam holds —
               UNCHANGED, and this chapter's T063/T065 followed its instruction:
               the mid-resume test asserts an ORDERING rather than an arrival,
               and splicing the buffering path in turns it red.
    20         two comment edits in `limits.ts` — UNCHANGED
    21         a second person — see below
    22         a rate-limit header assertion comparing seconds with `>` —
               UNCHANGED

## THE ONE THAT IS NOT NUMBERED, BECAUSE SEVEN CHAPTERS HAVE NUMBERED IT

**`specs/036-chapter-3-18/reader-protocol.md` has still not been run by a person.**

Chapters 3.14 through 3.20 each named this gap. 3.18 made it runnable — forty-five
minutes, six questions — and nobody ran it. **This chapter is the seventh to name
it and the first to put it in the task list (T108), which is not the same as
closing it.**

And this chapter is the strongest evidence yet for why it matters. Its most
expensive finding was not found by any checker: the feature was inert in the
product, and what found it was a test written against the deployed binary because
an analysis pass asked *what does the sealed client actually do* rather than *what
does a document say it does*. Every check in this repository compares bytes.

**Owner: a second person.** No command discharges this.
